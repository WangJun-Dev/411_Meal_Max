import pytest
from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal

@pytest.fixture()
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

@pytest.fixture
def mock_update_meal_stats(mocker):
    """Mock the update_meal_stats function for testing purposes."""
    return mocker.patch("meal_max.models.battle_model.update_meal_stats")

@pytest.fixture
def mock_get_random(mocker):
    """Mock the get_random function for testing purposes."""
    return mocker.patch("meal_max.models.battle_model.get_random")

"""Fixtures providing sample meals for the tests."""
@pytest.fixture
def sample_meal1():
    return Meal(1, 'Spaghetti', 'Italian', 12.99, 'MED')

@pytest.fixture
def sample_meal2():
    return Meal(2, 'Sushi', 'Japanese', 15.99, 'HIGH')

@pytest.fixture
def sample_combatants(sample_meal1, sample_meal2):
    return [sample_meal1, sample_meal2]

################################################## 
# Combatant Management Test Cases
##################################################

def test_prep_combatant(battle_model, sample_meal1):
    """Test adding a combatant to the battle."""
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].meal == 'Spaghetti'

def test_prep_combatant_full_list(battle_model, sample_combatants):
    """Test error when adding a combatant to a full list."""
    battle_model.combatants.extend(sample_combatants)
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(Meal(3, 'Pizza', 'Italian', 10.99, 'LOW'))

def test_clear_combatants(battle_model, sample_combatants):
    """Test clearing all combatants from the list."""
    battle_model.combatants.extend(sample_combatants)
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0

################################################## 
# Battle Test Cases
##################################################

def test_battle(battle_model, sample_combatants, mock_update_meal_stats, mock_get_random):
    """Test conducting a battle between two meals."""
    battle_model.combatants.extend(sample_combatants)
    mock_get_random.return_value = 0.4  # Set a fixed random number for testing

    winner = battle_model.battle()

    assert winner in ['Spaghetti', 'Sushi']
    assert len(battle_model.combatants) == 1
    mock_update_meal_stats.assert_called()

def test_battle_not_enough_combatants(battle_model):
    """Test error when trying to battle with insufficient combatants."""
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        battle_model.battle()

################################################## 
# Battle Score Test Cases
##################################################

def test_get_battle_score(battle_model, sample_meal1):
    """Test calculating the battle score for a meal."""
    score = battle_model.get_battle_score(sample_meal1)
    expected_score = (12.99 * len('Italian')) - 2  # price * len(cuisine) - difficulty_modifier
    assert score == pytest.approx(expected_score, 0.01)

################################################## 
# Combatant Retrieval Test Cases
##################################################

def test_get_combatants(battle_model, sample_combatants):
    """Test retrieving the current list of combatants."""
    battle_model.combatants.extend(sample_combatants)
    combatants = battle_model.get_combatants()
    assert len(combatants) == 2
    assert combatants[0].meal == 'Spaghetti'
    assert combatants[1].meal == 'Sushi'
