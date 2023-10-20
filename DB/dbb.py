import csv
import random
import hashlib
import math
import words

# ~~~ Modifiable ~~~
filename = "dummy_list.csv"
test_mode = False # If enabled will print the output to console instead of writing to a csv file
verbose = True # If enabled will print out bands and venues to the console
band_count = 30
venue_count = 10
event_count = 20
event_band_min = 1
event_band_max = 5

# How flexible will venues be when it comes to who they let perfom
genre_radius_min = 0.5 
genre_radius_max = 1.0 

# If enabled will use a fake physical value to represent band mobility
physical_enabled = True 
grid_size = [10.0, 10.0]
band_min_mobility_radius = 2.0 # Not technically a radius for now, but w/e
band_max_mobility_radius = 6.0 

genre_list = [
    "Classical",
    "Jazz",
    "Blues",
    "Rock",
    "Punk",
    "Metal",
    ]


# ~~~ Don't touch me ~~~
id_counter = 0

UP = 1
STAY = 0
DOWN = -1
SUCCESS = True
FAILURE = False

csv_fields = [
    "event_id",
    "venue",
    "bands",
    "genre_bottom",
    "genre_top",
    "max_bands",
]

def new_id():
    global id_counter
    id_counter +=1
    h = hashlib.sha1(bytes(id_counter)).hexdigest() 
    return "e"+h[:10]

def new_genre_score():
    # Pick a random number from 0 to length
    return random.uniform(0, len(genre_list))

def get_genres(score, radius):
    out = []
    i = 0
    while i < len(genre_list):
        if i >= score-radius and i <= score+radius:
            out.append(genre_list[i])
        i+=1 

def is_within(locA, radius, locB):
    # Checks if A is within radius of B
    # I'm too lazy to do the actual trig required for a circle, so for now be happy with a box lol

    # x axis
    if not locA[0] > locB[0] - radius or not locA[0] < locB[0] + radius:
        return False
    
    # y axis
    if not locA[1] > locB[1] - radius or not locA[1] < locB[1] + radius:
        return False

    return True

class Band_Manager:
    def __init__(self):
        self.bands = []

    def bsearch_by_genre_score(self, inc):
        start = 0
        l = len(self.bands)
        end = l-1
        safety = 0

        if end == -1:
            return 0
            
        while True:
            safety += 1
            if safety > l:
                print("ERROR: BSEARCH LOOP PROBLEM")
                quit()

            target = math.ceil((end - start)/2)+start

            dir = STAY
            if inc > self.bands[target].genre_score:
                dir = UP
            elif inc < self.bands[target].genre_score:
                dir = DOWN

            if dir == UP:
                # Check for finished or not
                if target == end:
                    return target+1

                # Not finished, modify params and continue
                start = target+1
                continue

            elif dir == DOWN:
                # Check for finished or not
                if target == start:
                    return target

                # Not finished, modify params and continue
                end = target-1
                continue

                
            if dir == STAY:
                # Just insert at place
                return target

    def store_band(self, inc):
        # Store bands in order based on genre score
        self.bands.insert(self.bsearch_by_genre_score(inc.genre_score), inc)
       

    def get_bands_by_genre_score(self, bottom_score, top_score):
        # Get a list of bands that are within the specified parameters
        bottom_range = self.bsearch_by_genre_score(bottom_score)
        top_range = self.bsearch_by_genre_score(top_score)
        return self.bands[bottom_range:top_range]


past_events = []
def generate_csv():
    with open(filename, "w") as csvfile:
        writer = csv.DictWriter(csvfile, delimiter=",", fieldnames = csv_fields)
        writer.writeheader()

        for pe in past_events:
            writer.writerow(pe.generate_dict())

def preview_csv():
      for pe in past_events:
        print(pe.generate_dict())
    


class Venue:
    def __init__(self):
        # Assign the venue a name. Hopefully this is enough to prevent overlap lol
        self.name = words.get_adj()+words.get_adj()+words.get_noun()

        # Assign the venue a genre value
        self.genre_score = new_genre_score()

        # Assign a specificity value (radius)
        self.genre_radius = random.uniform(genre_radius_min, genre_radius_max)

        # Assign a location
        self.location = [random.uniform(0, grid_size[0]), random.uniform(0, grid_size[1])]

        if verbose:
            print("V:", self.name, self.genre_score-self.genre_radius, self.genre_score+self.genre_radius, self.location)

    def host_event(self, bands):
        event = Event(self)
        event.populate_bands(bands)
        if len(event.bands) == 0:
            return False
        else:
            # Store event, this is bad and should be internal, but w/e
            past_events.append(event)
            return True

class Event:
    def __init__(self, v):
        self.id = new_id()
        self.venue = v
        self.bands = []

        # Generate the genre radius for this event
        self.genre_bottom = random.uniform(venue.genre_score-venue.genre_radius, venue.genre_score)
        self.genre_top = random.uniform(venue.genre_score, venue.genre_score+venue.genre_radius)

        # Assign max bands
        self.max_bands = random.randint(event_band_min, event_band_max)

    def populate_bands(self, band_man):
        # Look for bands that match the genre close enough to play the event
        layer1 = band_man.get_bands_by_genre_score(self.genre_bottom, self.genre_top)
        layer2 = []

        if physical_enabled:
            # Narrow bands down by location
            for band in layer1:
                if is_within(self.venue.location, band.radius, band.location):
                    layer2.append(band)
        else:
            layer2 = layer1

        '''
        print("POP EVENT", self.id, self.genre_bottom, self.genre_top)
        for b in potential:
            print("POTENTIAL BAND:", b.name, b.genre_score)
        '''

        c = 0
        while c < self.max_bands:
            l = len(layer2)
            if l == 0:
                break
            self.bands.append(layer2.pop(random.randint(0, l-1)))
            c+=1
        return

    def generate_dict(self):
        bands = []
        for band in self.bands:
            bands.append(band.name)
        return {
            "event_id": self.id,
            "venue": self.venue.name,
            "bands": bands,
            "genre_bottom": self.genre_bottom,
            "genre_top": self.genre_top,
            "max_bands": self.max_bands,
        }


class Band:
    def __init__(self):
        # Assign the band a name
        self.name = words.get_adj()+words.get_adj()+words.get_noun()

        # Assign the band a genre value
        self.genre_score = new_genre_score()

        # Assign mobility
        self.location = [random.uniform(0, grid_size[0]), random.uniform(0, grid_size[1])]
        self.radius = random.uniform(band_min_mobility_radius, band_max_mobility_radius)


venues = []


# Create band manager
bands_man = Band_Manager()

# Spawn bands
i = 0
while i < band_count:
    band = Band()
    bands_man.store_band(band)
    i += 1

if verbose:
    for b in bands_man.bands:
        print("B:", b.name, b.genre_score, b.location, b.radius)

# Spawn venues
i = 0
while i < venue_count:
    venue = Venue()
    venues.append(venue)
    i += 1

# Have events
i = 0
f = 0
while i < event_count:
    # Pick a random venue
    venue = venues[random.randint(0, len(venues)-1)]
    result = venue.host_event(bands_man)
    if result == SUCCESS:
        i += 1
    else:
        # Safety
        f += 1
        if i+1*3 < f:
            print("ERROR: TOO MANY FAILED EVENTS")
            quit()

if test_mode:
    preview_csv()
else:
    generate_csv()

