from django.shortcuts import render
import folium
from .route import Router
from .loadOsm import LoadOsm
from .toexcel import saveToXlsx


def showmap(request):
    return render(request, 'showmap.html')


def showroute(request, lat1, long1, lat2, long2, machineweight, machineheight, machinewidth):
    figure = folium.Figure()
    lat_1, long_1, lat_2, long_2 = float(lat1), float(long1), float(lat2), float(long2)
    machine_weight, machine_height, machine_width = float(machineweight), float(machineheight), float(machinewidth)
    data = LoadOsm("car", machine_weight, machine_height, machine_width)
    start = data.findNode(lat_1, long_1)
    end = data.findNode(lat_2, long_2)
    router = Router(data)
    result, route = router.doRoute(start, end)
    m = folium.Map(location=[((data.rnodes[start][0]) + (data.rnodes[end][0])) / 2,
                             ((data.rnodes[start][1]) + (data.rnodes[end][0])) / 2], zoom_start=10)
    points = []
    xlsx_data = []
    prew_node = start
    prew_name = ''
    for i in route:
        points.append(data.rnodes[i])
        for nodes in data.lines:
            if prew_node != start and i in nodes['data'] and prew_node in nodes['data']:
                if prew_name != nodes['name']:
                    xlsx_data.append({
                        'id': nodes['id'],
                        'lat': data.rnodes[i][0],
                        'long': data.rnodes[i][1],
                        'street': nodes['name']
                    })
                    print(nodes['id'], 'В точке', data.rnodes[i], 'поворот на', nodes['name'])
                    prew_name = nodes['name']
        prew_node = i
    saveToXlsx(data.rnodes[start], data.rnodes[end], xlsx_data)
    m.fit_bounds(points)
    m.add_to(figure)

    folium.PolyLine(points, weight=8, color='blue', opacity=0.6).add_to(m)
    folium.Marker(location=[(data.rnodes[start][0]), (data.rnodes[start][1])],
                  icon=folium.Icon(icon='play', color='green')).add_to(m)
    folium.Marker(location=[(data.rnodes[end][0]), (data.rnodes[end][1])],
                  icon=folium.Icon(icon='stop', color='red')).add_to(m)
    figure.render()
    context = {'map': figure}
    return render(request, 'showroute.html', context)
