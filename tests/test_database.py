# tests/test_database.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from unittest.mock import patch, MagicMock, call

class TestDatabaseConnection:
    @patch("database.db.psycopg2.connect")
    def test_get_db_connection_called_with_config(self, mock_connect):
        from database.db import get_db_connection, PG_CONFIG
        get_db_connection()
        mock_connect.assert_called_once_with(**PG_CONFIG)

    @patch("database.db.psycopg2.connect")
    def test_connection_failure_raises(self, mock_connect):
        mock_connect.side_effect = Exception("Connection refused")
        from database.db import get_db_connection
        with pytest.raises(Exception, match="Connection refused"):
            get_db_connection()

class TestInfluxWrite:
    @patch("database.db.InfluxDBClient")
    def test_write_sensor_called(self, mock_client_cls):
        mock_client   = MagicMock()
        mock_write_api = MagicMock()
        mock_client.write_api.return_value = mock_write_api
        mock_client_cls.return_value = mock_client

        from database.db import write_sensor_to_influx
        data = {"region": "Sylhet", "source": "IoT",
                "rainfall_mm": 80, "wind_speed_kmh": 30,
                "river_level_m": 6, "temperature_c": 32, "humidity": 70}
        write_sensor_to_influx(data)
        assert mock_write_api.write.called

    @patch("database.db.InfluxDBClient")
    def test_write_handles_exception_gracefully(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client.write_api.side_effect = Exception("InfluxDB down")
        mock_client_cls.return_value = mock_client

        from database.db import write_sensor_to_influx
        # Should not raise, just print the error
        write_sensor_to_influx({"region": "Dhaka", "rainfall_mm": 50,
                                 "wind_speed_kmh": 20, "river_level_m": 4,
                                 "temperature_c": 30, "humidity": 60})

class TestPostgresWrite:
    @patch("database.db.get_db_connection")
    def test_risk_written_to_postgres(self, mock_conn_fn):
        mock_conn = MagicMock()
        mock_cur  = MagicMock()
        mock_cur.fetchone.return_value = None
        mock_conn.cursor.return_value  = mock_cur
        mock_conn_fn.return_value = mock_conn

        from database.db import write_risk_to_postgres
        impact = {"estimated_affected": 1000, "estimated_displaced": 300,
                  "crop_damage_crore_bdt": 50, "economic_loss_crore_bdt": 200}
        write_risk_to_postgres("সিলেট", "flood", 0.85, "high", impact)
        assert mock_cur.execute.called
        assert mock_conn.commit.called

    @patch("database.db.get_db_connection")
    def test_rollback_on_error(self, mock_conn_fn):
        mock_conn = MagicMock()
        mock_cur  = MagicMock()
        mock_cur.execute.side_effect = Exception("DB error")
        mock_conn.cursor.return_value = mock_cur
        mock_conn_fn.return_value = mock_conn

        from database.db import write_risk_to_postgres
        write_risk_to_postgres("Dhaka", "cyclone", 0.6, "medium", {})
        assert mock_conn.rollback.called
