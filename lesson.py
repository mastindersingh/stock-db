# lessons.py
class Lesson:
    def __init__(self, title, content, author=None, date_posted=None):
        self.title = title
        self.content = content
        self.author = author
        self.date_posted = date_posted

# Create an empty list to store lessons
lessons = []

# Function to add a new lesson
def add_lesson(title, content, author=None, date_posted=None):
    lesson = Lesson(title, content, author, date_posted)
    lessons.append(lesson)

# Example lessons
add_lesson("Introduction to Stock Trading", "Content for lesson 1...", "Author Name", "Date")
add_lesson("Understanding Stock Market Trends", "Content for lesson 2...", "Author Name", "Date")
# Add more lessons as needed

