import tobii_research as tr
import time
from datetime import datetime,timedelta,timezone
import csv

# code used to check the time of the systems

# # Find the connected Tobii eye tracker
# eyetrackers = tr.find_all_eyetrackers()
# eyetracker = eyetrackers[0]

# # Function to handle gaze data and calculate time offset
# def gaze_data_callback(gaze_data):
#     # Get device time from the gaze data (in microseconds)
#     device_time = gaze_data['device_time_stamp']  # From Tobii
#     device_time_seconds = device_time / 1_000_000  # Convert to seconds

#     # Capture system time (in seconds) using time.time()
#     system_time = time.time()

#     # Calculate the difference between system time and device time
#     time_offset = system_time - device_time_seconds

#     # Convert device time to human-readable format
#     device_time_human = datetime.utcfromtimestamp(device_time_seconds).strftime('%Y-%m-%d %H:%M:%S.%f')

#     # Convert system time to human-readable format
#     system_time_human = datetime.utcfromtimestamp(system_time).strftime('%Y-%m-%d %H:%M:%S.%f')

#     # Print the times and offset
#     print(f"Device Time (Eye Tracker): {device_time_human}")
#     print(f"System Time (Computer): {system_time_human}")
#     print(f"Time Offset: {time_offset} seconds")

# # Subscribe to gaze data to capture device time
# eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)

# # Let the eye tracker collect gaze data for a while
# time.sleep(10)

# # Unsubscribe from gaze data
# eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)


# # Average time offset from your calculations (seconds)
# time_offset = 1727382579.016 # approximation

# # Path to your CSV file
# csv_file_path = 'output.csv'  # or 'centroid.csv'

# # Open the CSV file
# with open(csv_file_path, 'r') as file:
#     reader = csv.DictReader(file)
#     rows = list(reader)

# # Update each row with corrected device timestamps
# for row in rows:
#     # Convert the device_time_stamp from microseconds to seconds
#     device_time_stamp = int(row['device_time_stamp']) / 1_000_000

#     # Adjust by adding the time offset
#     corrected_time_seconds = device_time_stamp + time_offset

#     # Convert to human-readable format
#     row['device_time_stamp'] = datetime.utcfromtimestamp(corrected_time_seconds).strftime('%Y-%m-%d %H:%M:%S.%f')

# # Write the updated data back to a new CSV
# with open('output_corrected.csv', 'w', newline='') as file:
#     writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
#     writer.writeheader()
#     writer.writerows(rows)

# print("Device timestamps corrected and saved to 'output_corrected.csv'")
# print(873738329218-869646283552)
# print(873738487675-869646442021)
# import tobii_research as tr
# date_list= []
# gaze_list=[]

# # Callback function to handle gaze data
# def gaze_data_callback(gaze_data):
#     # Get the timestamp from the device
#     timestamp = gaze_data['device_time_stamp']
#     print(f"Current device time (microseconds): {timestamp}")
#     gaze_list.append(timestamp)
#     start_time_str = (datetime.now())
#     print(start_time_str)
#     date_list.append(start_time_str)
    
#     # start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc).timestamp()
#     # adjusted_start_time = int((start_time +4*3600) * 1_000_000 )
#     # print("here",adjusted_start_time)

# # Find all connected eye trackers
# eye_trackers = tr.find_all_eyetrackers()

# if eye_trackers:
#     # Select the first connected eye tracker
#     eye_tracker = eye_trackers[0]

#     # Subscribe to gaze data to retrieve timestamps
#     eye_tracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)

#     # Allow the program to run and collect data for a few seconds
#     import time
#     time.sleep(1)

#     # Unsubscribe after done
#     eye_tracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
# else:
#     print("No eye tracker found.")


# print(date_list[-1])

# print(gaze_list[-1])
# print(int(date_list[-1].timestamp() * 1000000))
# print(int(date_list[0].timestamp() * 1000000) -gaze_list[0] )

# device_time_human = datetime.utcfromtimestamp(int(2099126446922)/ 1_000_000).strftime('%Y-%m-%d %H:%M:%S.%f')
# print(device_time_human)
# print(datetime.now())

# Define the time offset (miliseconds)
#4092045666 for device and system
time_offset = 1734301927000000#1727382578857459



# Define the start and end times in the format: year, month, date, hour, minute, second
start_time_str = '2024-12-15 21:48:21' 
end_time_str = '2024-12-15 21:48:31'  

# start time 1734304644
# end time 1734304674

# Convert these strings to Unix timestamps (seconds since epoch)
start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc).timestamp()

end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc).timestamp()

print(start_time,end_time)

# Apply the time offset to start and end times
adjusted_start_time_m = int((start_time +5*3600) * 1_000_000 ) 
adjusted_end_time_m = int((end_time+5*3600) * 1_000_000)  
print(adjusted_start_time_m )
print(adjusted_end_time_m )

# print( 2717710759 - )

adjusted_start_time = int((start_time +5*3600) * 1_000_000 ) - time_offset
adjusted_end_time = int((end_time+5*3600) * 1_000_000)  - time_offset

# adjusted_start_time =869646442021
# adjusted_end_time = 873738487675
print(adjusted_start_time,adjusted_end_time)


input_csv_file = 'centroids.csv'
output_csv_file = 'time_centroids.csv'

input_csv_file_two = 'output.csv'
output_csv_file_two = 'time_outputs.csv'

input_csv_file_three = 'filtered_output.csv'
output_csv_file_three = 'time_filtered_outputs.csv'

# # Open the input CSV and filter the rows based on the adjusted time range
# with open(input_csv_file, 'r') as infile:
#     reader = csv.DictReader(infile)
    
#     # Create a list of filtered rows
#     filtered_rows = []
#     for row in reader:
#         # Convert device_time_stamp from microseconds to seconds
#         device_time_stamp_seconds = int(row['device_time_stamp']) 
        
#         # Check if the timestamp falls within the adjusted range
#         if adjusted_start_time <= device_time_stamp_seconds <= adjusted_end_time:
#             filtered_rows.append(row)

            # Open the input CSV and filter the rows based on the adjusted time range
with open(input_csv_file, 'r') as infile:
    reader = csv.DictReader(infile)
    

    filtered_rows = []
    for row in reader:

        device_time_stamp_seconds_start = int(row['start']) 
        device_time_stamp_seconds_end = int(row['end']) 
        
        if adjusted_start_time <= device_time_stamp_seconds_start and device_time_stamp_seconds_end <= adjusted_end_time:
            filtered_rows.append(row)


with open(output_csv_file, 'w', newline='') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
    writer.writeheader()
    writer.writerows(filtered_rows)

print(f"Filtered rows saved to {output_csv_file}")

with open(input_csv_file_two, 'r') as infile:
    reader = csv.DictReader(infile)
    

    filtered_rows = []
    for row in reader:

        device_time_stamp_seconds_start = int(row['device_time_stamp']) 
        device_time_stamp_seconds_end = int(row['device_time_stamp']) 
        
        if adjusted_start_time <= device_time_stamp_seconds_start and device_time_stamp_seconds_end <= adjusted_end_time:
            filtered_rows.append(row)


with open(output_csv_file_two, 'w', newline='') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
    writer.writeheader()
    writer.writerows(filtered_rows)

print(f"Filtered rows saved to {output_csv_file_two}")

with open(input_csv_file_three, 'r') as infile:
    reader = csv.DictReader(infile)
    

    filtered_rows = []
    for row in reader:

        device_time_stamp_seconds_start = int(row['start']) 
        device_time_stamp_seconds_end = int(row['end']) 
        
        if adjusted_start_time <= device_time_stamp_seconds_start and device_time_stamp_seconds_end <= adjusted_end_time:
            filtered_rows.append(row)


with open(output_csv_file_three, 'w', newline='') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
    writer.writeheader()
    writer.writerows(filtered_rows)

print(f"Filtered rows saved to {output_csv_file_three}")



