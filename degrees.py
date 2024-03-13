import csv
import sys

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}

def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass

def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"
    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")

def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    movie_people_frontier = []
    explored = []
    if source == target:
        return explored
    starting_neighbors = neighbors_for_person(source)
    for (movie, person) in starting_neighbors:
        if person == target:
            return [(movie, person)] 
        elif person==source: #don't add source to frontier
            pass
        else:
            movie_people_frontier.append([source, (movie, person)])
    
    while len(movie_people_frontier) != 0:
        #select first item
        [a, (m, p)] = movie_people_frontier[0]
        #add item to explored
        explored.append([a, (m, p)])
        # get neighbors for item
        new_neighbors = neighbors_for_person(p)
        new_neighbors2=[]
        for item in new_neighbors:
            new_neighbors2.append([p, item])
        #put source, frontier, and explored people in a list
        listofpeople=[str(source)]
        for [a, (m, p)] in movie_people_frontier:
            listofpeople.append(p)
        for [a, (m, p)] in explored:
            listofpeople.append(p)        
        for [adult, (movie, person)] in new_neighbors2:
            if person == target:
                explored.append([adult, (movie, person)])
                path=[]
                backtrack=explored
                backtrack.reverse()
                listofpathpeople=[str(target)]
                while listofpathpeople[-1] != str(source):
                    for x in range(0, len(backtrack)):
                        if listofpathpeople[-1] == backtrack[x][1][1]:
                            listofpathpeople.append(backtrack[x][0])
                listofpathpeople.reverse()
                for y in range(0, len(listofpathpeople)-1):
                    for x in range(0, len(explored)):
                        if explored[x][0] == listofpathpeople[y] and explored[x][1][1] == listofpathpeople[y+1]:
                            path.append(explored[x][1])
                return path
            elif person in listofpeople: # don't add the same person back in
                pass
            else:
                movie_people_frontier.append([adult, (movie, person)])
        movie_people_frontier.remove(movie_people_frontier[0])

def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]

def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors

if __name__ == "__main__":
    main()
