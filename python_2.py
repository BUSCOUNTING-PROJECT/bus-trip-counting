import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import os

def process_file2(file_path):
    # import excel file by user
    df1 = pd.read_excel(file_path, header=None)

    # Select relevant data
    selected_data1 = df1.iloc[19:, [3, 6, 7, 9]]
    selected_data1 = selected_data1.iloc[:-1]
    selected_data1.iloc[1:] = selected_data1.iloc[1:].sort_values(by=selected_data1.columns[0])

    # Save the selected data as a new excel file
    new_folder = '/Users/admin/Desktop/DLT/Counting Bus Trip/Counting/Web_Developer/output_file'
    file_dir, file_name = os.path.split(file_path)
    file_base, file_ext = os.path.splitext(file_name)
    edited_file_name = f"{file_base} edit{file_ext}"
    output_path1 = os.path.join(new_folder, edited_file_name)
    selected_data1.to_excel(output_path1, index=False, header=False)
    print("สร้างไฟล์ใหม่เสร็จเรียบร้อย:", output_path1)

    # Read the saved file and create GeoDataFrame
    data1 = pd.read_excel(output_path1)
    geometry1 = [Point(xy) for xy in zip(data1['long'], data1['lat'])]
    geo_df1 = gpd.GeoDataFrame(data1, geometry=geometry1)
    geo_df1.set_crs(epsg=4326, inplace=True)

    # Define the rest stop/area and radius
    center_lat1, center_lon1 = 13.87213236123334, 100.59487133474555
    center_lat2, center_lon2 = 13.738484105714624, 100.51632471176949
    center_lat3, center_lon3 = 13.739415765731161, 100.51624146924918
    center_lat4, center_lon4 = 13.870681313166788, 100.59364791655578
    center_lat5, center_lon5 = 14.678880911997199, 100.51130070461858 #แก้อู่
    radius_meters = 200

    # Create center points and buffer areas
    center_point1 = gpd.GeoDataFrame(geometry=[Point(center_lon1, center_lat1)], crs="EPSG:4326").to_crs(epsg=32647)
    center_point2 = gpd.GeoDataFrame(geometry=[Point(center_lon2, center_lat2)], crs="EPSG:4326").to_crs(epsg=32647)
    center_point3 = gpd.GeoDataFrame(geometry=[Point(center_lon3, center_lat3)], crs="EPSG:4326").to_crs(epsg=32647)
    center_point4 = gpd.GeoDataFrame(geometry=[Point(center_lon4, center_lat4)], crs="EPSG:4326").to_crs(epsg=32647)
    center_point5 = gpd.GeoDataFrame(geometry=[Point(center_lon5, center_lat5)], crs="EPSG:4326").to_crs(epsg=32647)
    
    radius_circle1 = gpd.GeoDataFrame(geometry=center_point1.buffer(radius_meters))
    radius_circle2 = gpd.GeoDataFrame(geometry=center_point2.buffer(radius_meters))
    radius_circle3 = gpd.GeoDataFrame(geometry=center_point3.buffer(radius_meters))
    radius_circle4 = gpd.GeoDataFrame(geometry=center_point4.buffer(radius_meters))
    radius_circle5 = gpd.GeoDataFrame(geometry=center_point5.buffer(radius_meters))
    geo_df1 = geo_df1.to_crs(radius_circle1.crs)

    # Count Function
    def count_exits_with_timestamps(df, radius1, radius2, radius3, radius4, radius5):
        exit_count_1_to_2, exit_count_3_to_4, exit_count_5 = 0, 0, 0
        transitions = []

        in_radius_1 = df.iloc[0].geometry.within(radius1.geometry[0])
        in_radius_3 = df.iloc[0].geometry.within(radius3.geometry[0])
        in_radius_5 = df.iloc[0].geometry.within(radius5.geometry[0])

        in_transition_1_to_2, in_transition_3_to_4 = False, False

        for index, row in df.iterrows():
            timestamp = row['ts']

            point_within_1 = row.geometry.within(radius1.geometry[0])
            point_within_2 = row.geometry.within(radius2.geometry[0])
            point_within_3 = row.geometry.within(radius3.geometry[0])
            point_within_4 = row.geometry.within(radius4.geometry[0])
            point_within_5 = row.geometry.within(radius5.geometry[0])

            if in_radius_1 and not point_within_1:
                in_radius_1 = False
                in_transition_1_to_2 = True
                transitions.append(("Exit Radius 1", timestamp))

            elif in_transition_1_to_2 and point_within_2:
                exit_count_1_to_2 += 1
                in_transition_1_to_2 = False
                transitions.append(("Enter Radius 2", timestamp))

            if in_radius_3 and not point_within_3:
                in_radius_3 = False
                in_transition_3_to_4 = True
                transitions.append(("Exit Radius 3", timestamp))

            elif in_transition_3_to_4 and point_within_4:
                exit_count_3_to_4 += 1
                in_transition_3_to_4 = False
                transitions.append(("Enter Radius 4", timestamp))
            
            if not in_radius_1 and point_within_1:
                    in_radius_1 = True
            if not in_radius_3 and point_within_3:
                    in_radius_3 = True
            
            if in_radius_5 and not point_within_5:
                exit_count_5 += 1
                transitions.append(("Exit Radius 5", timestamp))
                in_radius_5 = False
            elif not in_radius_5 and point_within_5:
                transitions.append(("Enter Radius 5", timestamp))
                in_radius_5 = True

        total_count = exit_count_1_to_2 + exit_count_3_to_4
        return exit_count_1_to_2, exit_count_3_to_4, exit_count_5, total_count, transitions

    exit_count_1_to_2, exit_count_3_to_4, exit_count_5, total_count, transitions = count_exits_with_timestamps(
        geo_df1, radius_circle1, radius_circle2, radius_circle3, radius_circle4, radius_circle5)

    print(f"Exit count from radius 1 to radius 2: {exit_count_1_to_2}")
    print(f"Exit count from radius 3 to radius 4: {exit_count_3_to_4}")
    print(f"Exit count from radius 5: {exit_count_5}")
    print(f"Total transitions: {total_count}")

    print("\nTransitions:")
    for event, time in transitions:
        print(f"{event} at {time}")

    def save_transitions_to_excel(transitions, total_count, file_name, folder_path):
        if not os.path.exists(folder_path):
             os.makedirs(folder_path)
        file_path = os.path.join(folder_path, file_name)
        df_transitions = pd.DataFrame(transitions, columns=["Event", "Timestamp"])
        df_total = pd.DataFrame({"Total Count": [total_count]})
        with pd.ExcelWriter(file_path) as writer:
            df_transitions.to_excel(writer, index=False, sheet_name="Transitions")
            df_total.to_excel(writer, index=False, sheet_name="Summary")
        print("Saved transitions to:", file_path)
        return file_path
    file_name = "output_summary.xlsx"
    output_folder = '/Users/admin/Desktop/DLT/Counting Bus Trip/Counting/Web_Developer/output_file'
    save_transitions_to_excel(transitions, total_count, file_name, output_folder)
    return total_count
print("count success")


