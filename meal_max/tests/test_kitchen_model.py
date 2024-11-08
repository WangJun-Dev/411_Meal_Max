from contextlib import contextmanager
import re
import sqlite3
import pytest
from meal_max.models.kitchen_model import (
    Meal,
    create_meal,
    delete_meal,
    get_leaderboard,
    get_meal_by_id,
    get_meal_by_name,
    update_meal_stats
)
######################################################
#
#    Fixtures
#
######################################################
def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn
    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)
    return mock_cursor
######################################################
#
#    Add and Delete Tests
#
######################################################
def test_create_meal(mock_cursor):
    create_meal(meal="Ramen", cuisine="Japanese", price=12.99, difficulty="MED")
    expected_query = normalize_whitespace("""
        INSERT INTO meals (meal, cuisine, price, difficulty)
        VALUES (?, ?, ?, ?)
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    
    assert actual_query == expected_query
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Ramen", "Japanese", 12.99, "MED")
    assert actual_arguments == expected_arguments
def test_create_meal_duplicate(mock_cursor):
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed")
    with pytest.raises(ValueError, match="Meal with name 'Ramen' already exists"):
        create_meal(meal="Ramen", cuisine="Japanese", price=12.99, difficulty="MED")
def test_create_meal_invalid_difficulty():
    with pytest.raises(ValueError, match="Invalid difficulty level: EASY. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal(meal="Ramen", cuisine="Japanese", price=12.99, difficulty="EASY")
def test_create_meal_invalid_price():
    with pytest.raises(ValueError, match="Invalid price: -12.99. Price must be a positive number."):
        create_meal(meal="Ramen", cuisine="Japanese", price=-12.99, difficulty="MED")
def test_delete_meal(mock_cursor):
    mock_cursor.fetchone.return_value = [False]
    
    delete_meal(1)
    expected_select_sql = normalize_whitespace("SELECT deleted FROM meals WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE meals SET deleted = TRUE WHERE id = ?")
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])
    assert actual_select_sql == expected_select_sql
    assert actual_update_sql == expected_update_sql
    expected_arguments = (1,)
    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]
    assert actual_select_args == expected_arguments
    assert actual_update_args == expected_arguments
    
def test_delete_meal_bad_id(mock_cursor):
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        delete_meal(999)
def test_delete_meal_already_deleted(mock_cursor):
    mock_cursor.fetchone.return_value = [True]
    with pytest.raises(ValueError, match="Meal with ID 999 has been deleted"):
        delete_meal(999)
######################################################
#
#    Get Meal
#
######################################################
def test_get_meal_by_id(mock_cursor):
    mock_cursor.fetchone.return_value = (1, "Ramen", "Japanese", 12.99, "MED", False)
    result = get_meal_by_id(1)
    expected_result = Meal(1, "Ramen", "Japanese", 12.99, "MED")
    assert result == expected_result
    expected_query = normalize_whitespace("""
        SELECT id, meal, cuisine, price, difficulty, deleted 
        FROM meals WHERE id = ?
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query
def test_get_meal_by_name(mock_cursor):
    mock_cursor.fetchone.return_value = (1, "Ramen", "Japanese", 12.99, "MED", False)
    result = get_meal_by_name("Ramen")
    expected_result = Meal(1, "Ramen", "Japanese", 12.99, "MED")
    assert result == expected_result
    expected_query = normalize_whitespace("""
        SELECT id, meal, cuisine, price, difficulty, deleted 
        FROM meals WHERE meal = ?
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query
def test_get_meal_by_bad_id(mock_cursor):
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        get_meal_by_id(999)
def test_get_meal_by_bad_name(mock_cursor):
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Meal with name Nonexistent Meal not found"):
        get_meal_by_name("Nonexistent Meal")
        
def test_get_leaderboard(mock_cursor):
    mock_cursor.fetchall.return_value = [
        (1, "Ramen", "Japanese", 12.99, "MED", 10, 7, 0.7),
        (2, "Udon", "Japanese", 11.99, "HIGH", 8, 5, 0.625)
    ]
    result = get_leaderboard(sort_by="wins")
    expected_result = [
        {
            'id': 1,
            'meal': "Ramen",
            'cuisine': "Japanese",
            'price': 12.99,
            'difficulty': "MED",
            'battles': 10,
            'wins': 7,
            'win_pct': 70.0
        },
        {
            'id': 2,
            'meal': "Udon",
            'cuisine': "Japanese",
            'price': 11.99,
            'difficulty': "HIGH",
            'battles': 8,
            'wins': 5,
            'win_pct': 62.5
        }
    ]
    assert result == expected_result
    expected_query = normalize_whitespace("""
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
        FROM meals WHERE deleted = false AND battles > 0 ORDER BY wins DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query
def test_update_meal_stats(mock_cursor):
    mock_cursor.fetchone.return_value = [False]
    update_meal_stats(1, "win")
    expected_select_sql = normalize_whitespace("SELECT deleted FROM meals WHERE id = ?")
    expected_update_sql = normalize_whitespace("""
        UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?
    """)
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])
    assert actual_select_sql == expected_select_sql
    assert actual_update_sql == expected_update_sql
def test_update_meal_stats_invalid_result(mock_cursor):
    mock_cursor.fetchone.return_value = [False]
    with pytest.raises(ValueError, match="Invalid result: draw. Expected 'win' or 'loss'."):
        update_meal_stats(1, "draw")