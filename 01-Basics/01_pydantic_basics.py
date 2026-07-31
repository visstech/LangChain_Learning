from pydantic import BaseModel 

class Student(BaseModel):
    name :str
    age:int
    course:str

student = Student(
    name="senthilkumar",
    age="50",
    course="AI Engineering"

)

print(student)
print(type(student.age))