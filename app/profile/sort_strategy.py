from abc import ABC, abstractmethod


class SortStrategy(ABC):
    # Returns
    # [Catagories]
    # Where catagories is the ordered list (Catagory Name, [ (Display value, Username) ,...])
    @abstractmethod
    def sort_users(self, list_users) -> list:
        pass


class AccessStrategy(SortStrategy):
    def sort_users(self, list_users):
        sorted_users = sorted(list_users, key=lambda x: (str(x.fName), str(x.sName)))
        user_groups = {"Student": [], "Coach": [],  "Admin": [], "Other": []}
        for user in sorted_users:
            user_format = [f"{user.fName} {user.sName}", user.username]
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
        users = [(f"{user.fName} {user.sName}", user.username) for user in sorted_users]
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
                yearGroups[schoolYr].append([f"{user.fName} {user.sName}", user.username])
            else:
                yearGroups['Other'].append([f"{user.fName} {user.sName}", user.username])
        data = []
        for key in yearGroups:
            if len(yearGroups[key]) > 0:
                data.append((key, yearGroups[key]))
        return data


class ShotsStrategy(SortStrategy):
    def sort_users(self, list_users):
        sorted_users = sorted(list_users, key=lambda x: (x.sName, x.fName))
        users = [(f"{user.fName} {user.sName}", user.username) for user in sorted_users]
        return "Users", users
