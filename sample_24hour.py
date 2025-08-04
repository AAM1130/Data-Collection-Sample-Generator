import pandas as pd
import datetime
import random


def generate_production_data(start_date, num_machines=6):
    """
    Generates a synthetic dataset for production machine data based on specified requirements.

    Args:
        start_date (datetime.date): The starting date for the data generation.
        num_machines (int): The total number of machines in the production environment.

    Returns:
        pandas.DataFrame: A DataFrame containing the generated production data.
    """

    data = []

    # Define machine IDs
    machine_ids = [f'M{i:03d}' for i in range(1, num_machines + 1)]

    # Define possible error codes
    error_codes = ['E001', 'E002', 'E003', 'E004', 'E005', 'E006', 'E007', 'E008', 'E009', 'E010']

    # Define shift details
    shifts = {
        1: {'start_hour': 8, 'end_hour': 16, 'active_machines': num_machines},  # 8 AM to 4 PM
        2: {'start_hour': 16, 'end_hour': 0, 'active_machines': num_machines - 2},  # 4 PM to 12 AM
        3: {'start_hour': 0, 'end_hour': 8, 'active_machines': num_machines - 3}  # 12 AM to 8 AM (next day)
    }

    # Lot numbers - at least two different lots
    lot_numbers = ['LOT_ABC_202507', 'LOT_XYZ_202508']
    current_lot_index = 0

    # Function to generate a random 6-digit product ID
    def generate_product_id():
        return f'P{random.randint(100000, 999999)}'

    # Initial product IDs for all machines
    machine_product_ids = {mid: generate_product_id() for mid in machine_ids}

    # Keep track of which machines change product ID at shift change
    machines_to_change_product = random.sample(machine_ids, 4)  # Select 4 machines to change product ID

    # Iterate through each shift for the 24-hour period
    for shift_num in [1, 2, 3]:
        shift_info = shifts[shift_num]

        # Determine the start and end datetime for the current shift
        if shift_num == 1:
            current_shift_start = datetime.datetime(start_date.year, start_date.month, start_date.day,
                                                    shift_info['start_hour'], 0, 0)
            current_shift_end = datetime.datetime(start_date.year, start_date.month, start_date.day,
                                                  shift_info['end_hour'], 0, 0)
        elif shift_num == 2:
            current_shift_start = datetime.datetime(start_date.year, start_date.month, start_date.day,
                                                    shift_info['start_hour'], 0, 0)
            current_shift_end = datetime.datetime(start_date.year, start_date.month,
                                                  start_date.day + (1 if shift_info['end_hour'] == 0 else 0),
                                                  shift_info['end_hour'], 0, 0)
        else:  # Shift 3
            current_shift_start = datetime.datetime(start_date.year, start_date.month, start_date.day + 1,
                                                    shift_info['start_hour'], 0, 0)
            current_shift_end = datetime.datetime(start_date.year, start_date.month, start_date.day + 1,
                                                  shift_info['end_hour'] + 8, 0, 0)  # 8 AM next day

        # Adjust for product ID changes at shift start for selected machines
        if shift_num != 1:  # Product ID changes happen at the start of Shift 2 and Shift 3
            for mid in machines_to_change_product:
                machine_product_ids[mid] = generate_product_id()
            # Randomly select new machines to change product ID for the next shift
            machines_to_change_product = random.sample(machine_ids, 4)

        # Randomly select active machines for the current shift
        active_machines_for_shift = random.sample(machine_ids, shift_info['active_machines'])

        # Assign unique operators for each active machine in the current shift
        operator_ids = [f'OP{random.randint(100, 999)}' for _ in active_machines_for_shift]
        machine_operator_map = dict(zip(active_machines_for_shift, operator_ids))

        # Change lot number at the start of Shift 2 (example logic)
        if shift_num == 2:
            current_lot_index = (current_lot_index + 1) % len(lot_numbers)

        # Simulate production for each active machine
        for machine_id in active_machines_for_shift:
            current_time = current_shift_start

            # Define break/lunch timings relative to shift start
            # Break 1: 2 hours into shift (120 minutes = 7200 seconds)
            # Lunch: 4 hours into shift (240 minutes = 14400 seconds)
            # Break 2: 6 hours into shift (360 minutes = 21600 seconds)

            break_times = {
                'break1_start': current_shift_start + datetime.timedelta(hours=2),
                'break1_end': current_shift_start + datetime.timedelta(hours=2, minutes=10),
                'lunch_start': current_shift_start + datetime.timedelta(hours=4),
                'lunch_end': current_shift_start + datetime.timedelta(hours=4, minutes=30),
                'break2_start': current_shift_start + datetime.timedelta(hours=6),
                'break2_end': current_shift_start + datetime.timedelta(hours=6, minutes=10)
            }

            while current_time < current_shift_end:
                # Check for breaks/lunch and add idle time
                if break_times['break1_start'] <= current_time < break_times['break1_end']:
                    current_time = break_times['break1_end']
                    continue
                if break_times['lunch_start'] <= current_time < break_times['lunch_end']:
                    current_time = break_times['lunch_end']
                    continue
                if break_times['break2_start'] <= current_time < break_times['break2_end']:
                    current_time = break_times['break2_end']
                    continue

                # Ensure current_time does not exceed shift end after breaks
                if current_time >= current_shift_end:
                    break

                # Randomly determine status (mostly 'Complete', sometimes 'Error')
                status = 'Complete'
                error_code = 'N/A'
                if random.random() < 0.05:  # 5% chance of error
                    status = 'Error'
                    error_code = random.choice(error_codes)

                # Random cycle time between 145 and 155 seconds
                cycle_time = random.randint(145, 155) if status == 'Complete' else 0

                data.append({
                    'Timestamp': current_time,
                    'Machine_ID': machine_id,
                    'Product_ID': machine_product_ids[machine_id],
                    'Lot_Number': lot_numbers[current_lot_index],
                    'Shift': shift_num,
                    'Cycle_Time_Seconds': cycle_time,
                    'Status': status,
                    'Error_Code': error_code,
                    'Operator_ID': machine_operator_map[machine_id]
                })

                # Advance time for the next cycle
                current_time += datetime.timedelta(seconds=cycle_time)

                # Add a small random gap to simulate machine load time or minor idle periods
                current_time += datetime.timedelta(seconds=random.randint(5, 15))

    df = pd.DataFrame(data)
    # Sort by timestamp for better readability
    df = df.sort_values(by='Timestamp').reset_index(drop=True)
    return df


# Generate data for a specific date
# You can change this date as needed
today = datetime.date(2025, 8, 1)
production_data_df = generate_production_data(today)

# Save DataFrame to a CSV file
output_filename = 'production_data.csv'
production_data_df.to_csv(output_filename, index=False)

print(f"Data successfully generated and saved to {output_filename}")
