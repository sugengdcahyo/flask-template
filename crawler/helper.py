from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta, MO


class Helper(object):
    def __init__(self):
        pass

    def date_parser(self, str_days_ago):
        TODAY = datetime.today()
        splitted = str_days_ago.split()

        if len(splitted) > 1:
            if splitted[1].lower() == 'tahun':
                date = TODAY - relativedelta(years=int(splitted[0]))
            elif splitted[1].lower() == 'bulan':
                date = TODAY - relativedelta(months=int(splitted[0]))
            elif splitted[1].lower() == 'minggu':
                date = TODAY - relativedelta(weeks=int(splitted[0]))
            elif splitted[1].lower() == 'hari':
                date = TODAY - relativedelta(days=int(splitted[0]))
            elif splitted[1].lower() == 'jam':
                date = datetime.now() - \
                    relativedelta(hours=int(splitted[0]))
            elif splitted[1].lower() == 'menit':
                date = datetime.now() - \
                    relativedelta(minutes=int(splitted[0]))
            elif splitted[1].lower() == 'detik':
                date = datetime.now() - \
                    relativedelta(seconds=int(splitted[0]))
            elif splitted[1].lower() == 'setahun':
                date = datetime.now() - relativedelta(years=1)
            elif splitted[1].lower() == 'sebulan':
                date = datetime.now() - relativedelta(months=1)
            elif splitted[1].lower() == 'seminggu':
                date = datetime.now() - relativedelta(weeks=1)
            elif splitted[1].lower() == 'sehari':
                date = datetime.now() - relativedelta(days=1)
            elif splitted[1].lower() == 'sejam':
                date = datetime.now() - relativedelta(hours=1)
            else:
                date = datetime.now()
        else:
            return str(TODAY.isoformat())

        return str(date.isoformat())

    def checkin_checkout_dates(self, days):
        start_date = datetime.now().date()
        end_date = (datetime.now() + timedelta(days=days)).date()

        dates = []

        while start_date < end_date:
            awal = start_date
            # increase day one by one
            start_date = start_date + timedelta(days=1)
            dates.append({"start": awal.strftime("%Y-%m-%d"),
                         "end": start_date.strftime("%Y-%m-%d")})

        return dates
    
    def define_local_category(self,name):
        room_name = name.lower()
        if "deluxe" in room_name or "deluks" in room_name:
            return "Deluxe Room"
        elif "superior" in room_name:
            return "Superior Room"
        elif 'family' in room_name or 'keluarga' in room_name:
            return "Family Room"
        elif "executive" in room_name or "eksekutif" in room_name:
            return "Executive Room"
        elif "junior" in room_name:
            return "Junior Suite"
        elif "standard" in room_name or "standar" in room_name or "king" in room_name or "queen" in room_name:
            return "Standard Room"
        elif "suite" in room_name:
            return "Suite Room"
        elif "room club" in room_name:
            return "Room Club"
        elif "twin" in room_name:
            return "Twin Room"
        elif "double" in room_name:
            return "Double Room"
        elif "single" in room_name:
            return "Single Room"
        else:
            return "Other"
