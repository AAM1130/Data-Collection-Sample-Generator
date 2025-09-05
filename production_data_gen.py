#
# Production Data Generator
#
# This script generates a synthetic dataset for a production environment based on
# a user-defined configuration file.
#
# Dependencies: pandas, toml
# Install with: pip install pandas toml
#

import pandas as pd
import datetime
import random
import toml
import os
import sys


def load_config(config_file="config.toml"):
    """
    Loads configuration settings from a TOML file.

    Args:
        config_file (str): The path to the TOML configuration file.

    Returns:
        dict: A dictionary of configuration settings.
    """
    if os.path.exists(config_file):
        print(f"Loading configuration from {config_file}...")
        with open(config_file, 'r') as f:
            return toml.load(f)
    else:
        print(f"Warning: {config_file} not found. Using default values.")
        return {}


def generate_production_data(config):
    """
    Generates a synthetic production dataset based on the provided configuration.

    Args:
        config (dict): A dictionary containing all the configuration settings.

    Returns:
        pandas.DataFrame: A DataFrame containing the generated production data.
    """
    # ------------------------------------------------
    # Define and load parameters with defaults
    # ------------------------------------------------
    work_cell_config = config.get('work_cell', {})
    first_machine_id = work_cell_config.get('first_machine_id', 'M001')
    machine_count = work_cell_config.get('machine_count', 6)
    default_machine_efficiency = work_cell_config.get('default_machine_efficiency', 95.0) / 100.0

    machine_efficiencies = config.get('machine_efficiencies', {})
    machine_efficiencies = {k: v / 100.0 for k, v in machine_efficiencies.items()}

    shifts_config = config.get('shifts', {})
    shift_schedule = shifts_config.get('shift_schedule', [
        {"name": "1st", "start_time": "08:00", "end_time": "16:00", "active_machines": 6},
        {"name": "2nd", "start_time": "16:00", "end_time": "00:00", "active_machines": 4},
        {"name": "3rd", "start_time": "00:00", "end_time": "08:00", "active_machines": 3}
    ])
    break_duration_minutes = shifts_config.get('break_duration_minutes', 10)
    lunch_duration_minutes = shifts_config.get('lunch_duration_minutes', 30)
    break_and_lunch_hours = shifts_config.get('break_and_lunch_times', [2, 4, 6])
    shift_startup_delay_seconds = shifts_config.get('shift_startup_delay_seconds', [30, 180])

    order_config = config.get('order', {})
    total_parts_to_produce = order_config.get('total_parts', 2000)
    base_cycle_time_seconds = order_config.get('base_cycle_time_seconds', 74.0)

    operators_config = config.get('operators', {})
    default_operator_efficiency = operators_config.get('default_operator_efficiency', 90.0) / 100.0
    base_handling_time_seconds = operators_config.get('base_handling_time_seconds', 5.0)
    resume_delay_seconds = operators_config.get('resume_delay_seconds', 120)
    operator_efficiency_variation = operators_config.get('operator_efficiency_variation_percentage', 5.0) / 100.0

    # ------------------------------------------------
    # Setup and Initialization
    # ------------------------------------------------
    data = []

    # Generate machine IDs based on the first_machine_id and count
    machine_ids = []
    prefix = first_machine_id[0]
    start_num = int(first_machine_id[1:])
    for i in range(machine_count):
        machine_ids.append(f'{prefix}{start_num + i:03d}')

    # Calculate machine cycle times based on their efficiency
    machine_cycle_times = {}
    for mid in machine_ids:
        efficiency = machine_efficiencies.get(mid, default_machine_efficiency)
        # Cycle time with efficiency loss
        machine_cycle_times[mid] = base_cycle_time_seconds / efficiency

    # Keep track of production counts and lot numbers
    parts_produced = 0
    current_lot = ""
    current_lot_num = 1

    # Initial operator assignments for all machines
    machine_operator_map = {}

    # ------------------------------------------------
    # Main Generation Loop
    # ------------------------------------------------
    start_date = datetime.date.today()
    current_time = datetime.datetime.combine(start_date, datetime.time.fromisoformat(shift_schedule[0]['start_time']))

    # Main loop runs until the total number of parts is produced
    while parts_produced < total_parts_to_produce:
        for shift in shift_schedule:
            shift_start_time = datetime.datetime.combine(current_time.date(),
                                                         datetime.time.fromisoformat(shift['start_time']))
            shift_end_time = datetime.datetime.combine(current_time.date(),
                                                       datetime.time.fromisoformat(shift['end_time']))
            if shift_end_time <= shift_start_time:
                shift_end_time += datetime.timedelta(days=1)

            # Change lot at midnight or start of 1st shift if total parts not met
            if current_lot == "" or shift_end_time.time().hour == 0:
                # Add a transition period for lot change
                lot_change_duration = datetime.timedelta(minutes=random.uniform(10, 15))
                current_time += lot_change_duration

                # Generate new lot number based on the date
                today_formatted = shift_end_time.strftime("%y%m%d")
                current_lot = f'MI{today_formatted}A{current_lot_num:02d}'
                current_lot_num += 1

            # Assign new unique operators for each active machine for the shift
            active_machines = random.sample(machine_ids, shift['active_machines'])
            for mid in active_machines:
                machine_operator_map[mid] = f'OP{random.randint(1000, 9999)}'

            # Define breaks and lunch for the current shift
            break_times = []
            for hour in break_and_lunch_hours:
                break_start = shift_start_time + datetime.timedelta(hours=hour)
                if hour == 4:  # Assuming 4-hour mark is lunch
                    break_end = break_start + datetime.timedelta(minutes=lunch_duration_minutes)
                else:
                    break_end = break_start + datetime.timedelta(minutes=break_duration_minutes)
                break_times.append((break_start, break_end))

            # Introduce a random startup delay for each machine at the beginning of the shift**
            machine_next_available_time = {}
            for mid in machine_ids:
                if mid in active_machines:
                    delay = random.uniform(shift_startup_delay_seconds[0], shift_startup_delay_seconds[1])
                    machine_next_available_time[mid] = shift_start_time + datetime.timedelta(seconds=delay)
                else:
                    machine_next_available_time[mid] = shift_end_time

            # Set the simulation time to the start of the shift
            current_time = shift_start_time

            while current_time < shift_end_time and parts_produced < total_parts_to_produce:

                # Find the next event time across all active machines
                next_event_time = shift_end_time
                for mid in active_machines:
                    next_event_time = min(next_event_time, machine_next_available_time.get(mid, shift_end_time))

                # Check for scheduled break/lunch times
                for b_start, b_end in break_times:
                    if b_start > current_time and b_start < next_event_time:
                        next_event_time = b_start

                # Move the simulation clock forward to the next event
                if next_event_time > current_time:
                    current_time = next_event_time

                if current_time >= shift_end_time:
                    break

                for machine_id in active_machines:
                    if machine_next_available_time[machine_id] > current_time:
                        continue

                    if parts_produced >= total_parts_to_produce:
                        break

                    # Check for break/lunch times and add a delay
                    on_break = False
                    for b_start, b_end in break_times:
                        if b_start <= current_time < b_end:
                            machine_next_available_time[machine_id] = b_end
                            on_break = True
                            break
                    if on_break:
                        continue

                    # Apply a small delay after breaks to simulate restart time
                    last_event_time = machine_next_available_time[machine_id]
                    for b_start, b_end in break_times:
                        if b_start <= last_event_time < b_end:
                            # A random delay is applied to simulate the restart after break/lunch
                            restart_delay = datetime.timedelta(
                                seconds=random.uniform(resume_delay_seconds * 0.8, resume_delay_seconds * 1.2))
                            current_time = current_time + restart_delay
                            machine_next_available_time[machine_id] = current_time
                            break

                    # Determine the total cycle time for this part
                    machine_cycle_time = machine_cycle_times[machine_id]

                    # Calculate operator handling time with per-cycle variation
                    variation_factor = random.uniform(1 - operator_efficiency_variation,
                                                      1 + operator_efficiency_variation)
                    operator_handling_time = (
                                                         base_handling_time_seconds / default_operator_efficiency) * variation_factor

                    total_cycle_time = machine_cycle_time + operator_handling_time

                    # Randomly determine status (mostly 'Complete', sometimes 'Error')
                    status = 'Complete'
                    error_code = 'N/A'
                    if random.random() < 0.05:  # 5% chance of error
                        status = 'Error'
                        error_code = random.choice(
                            ['E001', 'E002', 'E003', 'E004', 'E005', 'E006', 'E007', 'E008', 'E009', 'E010'])
                        total_cycle_time = random.uniform(30, 90)
                    else:
                        parts_produced += 1

                    # Add data entry
                    data.append({
                        'Timestamp': current_time,
                        'Machine_ID': machine_id,
                        'Product_ID': 111111111,  # Simplified for this generator
                        'Lot_Number': current_lot,
                        'Cycle_Time_Seconds': round(total_cycle_time, 2),
                        'Status': status,
                        'Error_Code': error_code,
                        'Operator_ID': machine_operator_map.get(machine_id, "N/A")
                    })

                    # Update next available time for this machine
                    machine_next_available_time[machine_id] = current_time + datetime.timedelta(
                        seconds=total_cycle_time)

            # If the loop finished before the shift ended, it's because the order was fulfilled
            if parts_produced >= total_parts_to_produce:
                break

    df = pd.DataFrame(data)
    df = df.sort_values(by='Timestamp').reset_index(drop=True)
    return df


if __name__ == '__main__':
    try:
        config = load_config()
        output_filename = config.get('output', {}).get('filename', 'production_data.csv')

        production_data_df = generate_production_data(config)

        if not production_data_df.empty:
            # Format the Timestamp column to remove milliseconds before saving
            production_data_df['Timestamp'] = production_data_df['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
            production_data_df.to_csv(output_filename, index=False)
            print(f"\nData successfully generated and saved to {output_filename}")
            print(f"Total parts produced: {len(production_data_df[production_data_df['Status'] == 'Complete'])}")
        else:
            print("\nFailed to generate data. Check your configuration settings.")

    except FileNotFoundError as e:
        print(f"Error: Required file not found. {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")