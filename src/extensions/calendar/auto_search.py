import os

import cream.path

def search_for_calendars():

    calendars = {}
    
    calendars['evolution'] = find_evolution_calendars()
    
    return calendars
    
    

def find_evolution_calendars():

    import evolution
    
    calendars = []
    data_home = cream.path.XDG_DATA_HOME[0]
    base_path = os.path.join(data_home, 'evolution/calendar')
    
    for name, path in evolution.ecal.list_calendars():
        path = path.replace('local:', '')
        path = os.path.join(base_path, path)
        cal_file = os.path.join(path, 'calendar.ics')
        
        if os.path.isfile(cal_file):
            calendar = {'name': name.decode('utf-8'),
                        'data': cal_file}
            calendars.append(calendar)
            
    return calendars
