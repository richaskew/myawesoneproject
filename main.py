import pandas as pd
import math
import tkinter as tk
from tkinter import messagebox, Entry, Label, Button
import folium
from geopy.geocoders import Nominatim
from tkinter import Frame

def haversine_distance(coord1, coord2):
    earth_radius = 6371.0

    lat1, lon1 = coord1
    lat2, lon2 = coord2

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat / 2.0) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(
        dlon / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = earth_radius * c
    return distance * 1000

def find_closest_defib(user_location, defib_data, search_radius=None):
    closest_distance = float('inf')
    closest_defib_location = None

    for _, row in defib_data.iterrows():
        defib_location = (row['lat'], row['long'])
        distance = haversine_distance(user_location, defib_location)

        if search_radius is not None and distance <= search_radius:
            if distance < closest_distance:
                closest_distance = distance
                closest_defib_location = defib_location
        elif search_radius is None:
            if distance < closest_distance:
                closest_distance = distance
                closest_defib_location = defib_location

    return closest_defib_location

def display_defib_list_in_radius(user_location, defib_data, search_radius):
    defibs_within_radius = []
    for _, row in defib_data.iterrows():
        defib_location = (row['lat'], row['long'])
        distance = haversine_distance(user_location, defib_location)
        if distance <= search_radius:
            defibs_within_radius.append({
                'name': row['unique_identifier'],
                'address': f"{row['address_line1']}, {row['address_city']}, {row['address_post_code']}",
                'coordinates': defib_location,
                'distance': distance
            })

    if defibs_within_radius:
        message = "Defibrillators within search radius:\n\n"
        for defib in defibs_within_radius:
            message += (
                f"Name: {defib['name']}\n"
                f"Address: {defib['address']}\n"
                f"Coordinates: {defib['coordinates']}\n"
                f"Distance: {defib['distance']} meters\n\n"
            )
        messagebox.showinfo("Defibrillators Within Radius", message)
    else:
        messagebox.showinfo("Defibrillators Within Radius", "No defibrillators found within the search radius.")

def show_defibrillator_info_with_radius():
    address = address_entry.get()
    search_radius = float(radius_entry.get()) if radius_entry.get() else None

    geolocator = Nominatim(user_agent="defibrillator_finder")

    try:
        location = geolocator.geocode(address)
        if location:
            user_location = (location.latitude, location.longitude)
            excel_file_path = r'C:\Users\User\Documents\defibrillator_data.xlsx'
            defib_data = pd.read_excel(excel_file_path)

            display_defib_list_in_radius(user_location, defib_data, search_radius)
            display_map(user_location, defib_data, search_radius)
        else:
            messagebox.showinfo("Error", "Could not find coordinates for the provided address.")
    except Exception as e:
        messagebox.showinfo("Error", f"An error occurred: {str(e)}")

def use_custom_address():
    address = address_entry.get()

    geolocator = Nominatim(user_agent="defibrillator_finder")

    try:
        location = geolocator.geocode(address)
        if location:
            user_location = (location.latitude, location.longitude)
            excel_file_path = r'C:\Users\User\Documents\defibrillator_data.xlsx'
            defib_data = pd.read_excel(excel_file_path)

            closest_defib_location = find_closest_defib(user_location, defib_data)

            if closest_defib_location:
                display_map(user_location, defib_data, None, closest_defib_location)
            else:
                messagebox.showinfo("Defibrillator Information", "No defibrillators found nearby.")
        else:
            messagebox.showinfo("Error", "Could not find coordinates for the provided address.")
    except Exception as e:
        messagebox.showinfo("Error", f"An error occurred: {str(e)}")


def display_map(user_location, defib_data, search_radius, closest_defib_location=None):
    m = folium.Map(location=user_location, zoom_start=15)

    folium.Marker(location=user_location, popup="Your Location").add_to(m)

    for _, row in defib_data.iterrows():
        defib_location = (row['lat'], row['long'])
        distance = haversine_distance(user_location, defib_location)
        if search_radius is None or (search_radius is not None and distance <= search_radius):
            color = "red" if defib_location == closest_defib_location else "blue"
            folium.Marker(location=defib_location, popup=row['address_line1'], icon=folium.Icon(color=color)).add_to(m)

    save_path = "map.html"
    m.save(save_path)
    import webbrowser
    webbrowser.open(save_path)


# gui
root = tk.Tk()
root.title("Defibrillator Finder")

frame = Frame(root, padx=40, pady=40)
frame.pack()

title_label = Label(frame, text="Find Closest Defibrillator", font=("Helvetica", 16, "bold"))
title_label.pack()

address_label = Label(frame, text="Enter the Postcode or the Closest street:", font=("Helvetica", 12))
address_label.pack(pady=5)
address_entry = Entry(frame, font=("Helvetica", 12))
address_entry.pack(pady=5)
radius_label = Label(frame, text="Enter Search Radius (meters):", font=("Helvetica", 12))
radius_label.pack(pady=5)
radius_entry = Entry(frame, font=("Helvetica", 12))
radius_entry.pack(pady=5)

custom_address_button = Button(frame, text="Display The Closest Defibrillator", font=("Helvetica", 12), command=use_custom_address)
custom_address_button.pack(pady=10)
custom_address_radius_button = Button(frame, text="Display The Closest Defibrillator with Radius", font=("Helvetica", 12), command=show_defibrillator_info_with_radius)
custom_address_radius_button.pack(pady=10)

root.mainloop()
