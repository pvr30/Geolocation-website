from django.shortcuts import render, get_object_or_404
from .models import Measurement
from .forms import MeasurementModelForm
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from .utils import get_geo, get_center_coordinates, get_zoom, get_ip_address
import folium
# Create your views here.

def create_distance(request):
     # initial values
    distance = None
    destination = None

    obj = get_object_or_404(Measurement, id=1)
    form = MeasurementModelForm(request.POST or None)
    geolocator = Nominatim(user_agent="measurement")


    # ip = get_ip_address(request)
    # print(ip)
    ip = '103.238.106.242'
    # ip = '72.14.207.99'
    county, city, lat, lon = get_geo(ip)
    # print('location country', county)
    # print('location city', city['city'])
    # print('location city', city)
    city = city['city']

    # print('location lat, lon', lat, lon)

    location = geolocator.geocode(city)
    # print(location)
    loc_lat = lat
    loc_lon = lon
    pointA = (loc_lat, loc_lon)

    map_ = folium.Map(width=800, height=500, location=get_center_coordinates(loc_lat, loc_lon), zoom_start=8)

    folium.Marker([loc_lat, loc_lon], tooltip='click here for more', popup=city,
                    icon=folium.Icon(color='purple')).add_to(map_)

    if form.is_valid():
        instance = form.save(commit=False)
        destination_ = form.cleaned_data.get('destination')
        destination = geolocator.geocode(destination_)
        # print(destination)
        # print(destination.latitude)
        des_lat = destination.latitude
        des_lon = destination.longitude
        pointB = (des_lat, des_lon)

        distance = round(geodesic(pointA, pointB).km, 2)

        map_ = folium.Map(width=800, height=500, location=get_center_coordinates(loc_lat, loc_lon, des_lat, des_lon), zoom_start=get_zoom(distance))

        folium.Marker([loc_lat, loc_lon], tooltip='click here for more', popup=city,
                    icon=folium.Icon(color='purple')).add_to(map_)

        folium.Marker([des_lat, des_lon], tooltip='click here for more', popup=destination,
                    icon=folium.Icon(color='red')).add_to(map_)

         # draw the line between location and destination
        line = folium.PolyLine(locations=[pointA, pointB], weight=5, color='blue')
        map_.add_child(line)

        instance.location = location
        instance.distance = distance
        instance.save()

    map_ = map_._repr_html_()

    data = {
        'distance': distance,
        'destination': destination,
        'form': form,
        'map': map_
    }
    return render(request, 'measurement/main.html', data)