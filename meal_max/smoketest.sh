#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
    case $1 in
        --echo-json) ECHO_JSON=true ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

###############################################
# Health checks
###############################################

check_health() {
    echo "Checking health status..."
    curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
    if [ $? -eq 0 ]; then
        echo "Service is healthy."
    else
        echo "Health check failed."
        exit 1
    fi
}

check_db() {
    echo "Checking database connection..."
    curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
    if [ $? -eq 0 ]; then
        echo "Database connection is healthy."
    else
        echo "Database check failed."
        exit 1
    fi
}

##########################################################
# Meal Management
##########################################################

clear_meals() {
    echo "Clearing all meals..."
    curl -s -X DELETE "$BASE_URL/clear-meals" | grep -q '"status": "success"'
    if [ $? -eq 0 ]; then
        echo "All meals cleared successfully."
    else
        echo "Failed to clear meals."
        exit 1
    fi
}

create_meal() {
    meal=$1
    cuisine=$2
    price=$3
    difficulty=$4
    echo "Creating meal: $meal ($cuisine, $price, $difficulty)..."
    curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":\"$difficulty\"}" | grep -q '"status": "success"'
    if [ $? -eq 0 ]; then
        echo "Meal created successfully."
    else
        echo "Failed to create meal."
        exit 1
    fi
}

delete_meal_by_id() {
  meal_id=$1

  echo "Deleting meal by ID ($meal_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
  if echo "$response" | grep -q '"status": "meal deleted"'; then
    echo "Meal deleted successfully by ID ($meal_id)."
  else
    echo "Failed to delete meal by ID ($meal_id)."
    exit 1
  fi
}

get_meal_by_id() {
  meal_id=$1

  echo "Getting meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by ID ($meal_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by ID ($meal_id)."
    exit 1
  fi
}
get_meal_by_name() {
    meal_name="$1"
    encoded_name=$(echo "$meal_name" | sed 's/ /%20/g')
    echo "Getting meal by name: $meal_name..."
    response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$encoded_name")
    echo "Raw response: $response"
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Meal retrieved successfully."
        if [ "$ECHO_JSON" = true ]; then
            echo "Meal JSON:"
            echo "$response"
        fi
    else
        echo "Failed to get meal. Response:"
        echo "$response"
        exit 1
    fi
}

##########################################################
# Battle Management
##########################################################

prep_combatant() {
    meal=$1
    echo "Prepping combatant: $meal..."
    curl -s -X POST "$BASE_URL/prep-combatant" -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\"}" | grep -q '"status": "success"'
    if [ $? -eq 0 ]; then
        echo "Combatant prepped successfully."
    else
        echo "Failed to prep combatant."
        exit 1
    fi
}

clear_combatants() {
    echo "Clearing all combatants..."
    curl -s -X POST "$BASE_URL/clear-combatants" | grep -q '"status": "success"'
    if [ $? -eq 0 ]; then
        echo "All combatants cleared successfully."
    else
        echo "Failed to clear combatants."
        exit 1
    fi
}

get_combatants() {
    echo "Getting combatants..."
    response=$(curl -s -X GET "$BASE_URL/get-combatants")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Combatants retrieved successfully."
        if [ "$ECHO_JSON" = true ]; then
            echo "Combatants JSON:"
            echo "$response" | jq .
        fi
    else
        echo "Failed to get combatants."
        exit 1
    fi
}

battle() {
    echo "Starting a battle..."
    response=$(curl -s -X GET "$BASE_URL/battle")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Battle completed successfully."
        if [ "$ECHO_JSON" = true ]; then
            echo "Battle result JSON:"
            echo "$response" | jq .
        fi
    else
        echo "Battle failed."
        exit 1
    fi
}

##########################################################
# Leaderboard
##########################################################

get_leaderboard() {
    echo "Getting meal leaderboard..."
    response=$(curl -s -X GET "$BASE_URL/leaderboard")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Leaderboard retrieved successfully."
        if [ "$ECHO_JSON" = true ]; then
            echo "Leaderboard JSON:"
            echo "$response" | jq .
        fi
    else
        echo "Failed to get leaderboard."
        exit 1
    fi
}

# Health checks
check_health
check_db

# Clear all meals
clear_meals

# Create meals
create_meal "Spaghetti Carbonara" "Italian" 12.99 "MED"
create_meal "Sushi Platter" "Japanese" 24.99 "HIGH"
create_meal "Chicken Tikka Masala" "Indian" 14.99 "MED"
create_meal "Caesar Salad" "American" 8.99 "LOW"
create_meal "Beef Bourguignon" "French" 22.99 "HIGH"

# Get meal by ID
get_meal_by_id 1

# Get meal by name
get_meal_by_name "Sushi Platter"

# Delete a meal
delete_meal 3

# Get leaderboard
get_leaderboard

# Clear combatants
clear_combatants

# Prep combatants
prep_combatant "Spaghetti Carbonara"
prep_combatant "Sushi Platter"

# Get combatants
get_combatants

# Battle
battle

# Clear combatants
clear_combatants

# Prep new combatants
prep_combatant "Caesar Salad"
prep_combatant "Beef Bourguignon"

# Battle again
battle

# Get updated leaderboard
get_leaderboard

echo "All tests passed successfully!"