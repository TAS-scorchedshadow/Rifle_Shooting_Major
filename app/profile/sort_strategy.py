from abc import ABC, abstractmethod

from app.api.api import num_shots


class SortStrategy(ABC):
    # Returns
    # [Catagories]
    # Where catagories is the ordered list (Catagory Name, [ (Display value, Sub display line, Username) ,...])
    @abstractmethod
    def sort_users(self, list_users) -> list:
        pass


class AccessStrategy(SortStrategy):
    def sort_users(self, list_users):
        sorted_users = sorted(list_users, key=lambda x: (str(x.fName), str(x.sName)))
        user_groups = {"Student": [], "Coach": [],  "Admin": [], "Other": []}
        for user in sorted_users:
            user_format = (f"{user.fName} {user.sName}", None, user.username)
            if user.access == 0:
                user_groups["Student"].append(user_format)
            elif user.access == 1:
                user_groups["Coach"].append(user_format)
            elif user.access == 2:
                user_groups["Admin"].append(user_format)
            else:
                user_groups["Other"].append(user_format)
        data = []
        for key in user_groups:
            if len(user_groups[key]) > 0:
                data.append((key, user_groups[key]))
        return data


class LastNameStrategy(SortStrategy):
    def sort_users(self, list_users):
        sorted_users = sorted(list_users, key=lambda x: (str(x.sName), str(x.fName)))
        users = [(f"{user.fName} {user.sName}", "Funny", user.username) for user in sorted_users]
        return [("Users", users)]


class YearStrategy(SortStrategy):
    def sort_users(self, list_users):
        sorted_users = sorted(list_users, key=lambda x: (str(x.fName), str(x.sName)))
        yearGroups = {'Year 12': [], 'Year 11': [], 'Year 10': [], 'Year 9': [], 'Year 8': [],
                      'Year 7': [], 'Other': []}
        for user in sorted_users:
            schoolYr = f"Year {user.get_school_year()}"
            print(schoolYr)
            if schoolYr in yearGroups:
                yearGroups[schoolYr].append([f"{user.fName} {user.sName}", None, user.username])
            else:
                yearGroups['Other'].append([f"{user.fName} {user.sName}", None, user.username])
        data = []
        for key in yearGroups:
            if len(yearGroups[key]) > 0:
                data.append((key, yearGroups[key]))
        return data


class ShotsStrategy(SortStrategy):
    def sort_users(self, list_users):
        first_sort = sorted(list_users, key=lambda x: (str(x.sName), str(x.fName)))
        users_shots = []
        for user in first_sort:
            res = num_shots(user.id, user.club.season_start, user.club.season_end)
            stages = res["num_stages"]
            shots = res["num_shots"]
            users_shots.append((user, stages, shots))
        users_shots.sort(key=lambda x: (x[1], x[2]), reverse=True)

        active_list = []
        inactive_list = []
        for user, stages, shots in users_shots:
            format = (f"{user.fName} {user.sName}", f"Stages {stages} - Shots {shots}", user.username)
            if stages == 0:
                inactive_list.append(format)
            else:
                active_list.append(format)
        return [("Active Shooters", active_list), ("Inactive Shooters", inactive_list)]
