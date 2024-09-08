

class ABStract:
    name:str
    age:int
    color = 'BLUE'

    def get_color(self):
        pass


class Mane(ABStract):
    name = 'Valera'
    age = 23

    def get_color(self):
        return super().get_color()

    def get_name(self):
        return Mane.name


class A:
    age = 2

class B:
    age = 3

    @classmethod
    def create_B(cls, age):
        r = cls()
        r.age = age
        return r

a = B.create_B(23)
print(a.age)
