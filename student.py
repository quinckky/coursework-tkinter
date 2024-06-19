class Student:
    
    def __init__(self, name: str, group: int, grades: list[int]):
        self._name = name
        self._group = group
        self._grades = grades
    
    @property
    def name(self):
        return self._name
    
    @property
    def group(self):
        return self._group
    
    @property
    def grades(self):
        return self._grades
    