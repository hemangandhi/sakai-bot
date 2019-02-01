from functools import wraps
import datetime as dt

import dateparser as dp

import sakai
from util import most_likely_match, clean_time

class Functionality:
    fns = dict()

    @staticmethod
    def add_function(args, name, docs):
        def wrapper(f):
            return Functionality(args, f, name, docs)
        return wrapper

    def __init__(self, args, function, name, docs):
        self.args = args
        self.function = function
        self.name = name
        self.docs = docs
        Functionality.fns[name] = self
    def __call__(self, *args):
        if len(args) not in self.args:
            return False, "{} is not a valid number of arguments".format(len(args))
        return self.function(*args)
    def __str__(self):
        return self.docs
    def __repr__(self):
        return self.docs

def usage(acc, special=''):
    template = '''
There were errors in your commands. Here is the accumulated output:
{}

USAGE: sakai [command] [then [command]]...
where command is one of:
{}
    '''

    commands = '\n'.join("\t{}: {}".format(k, Functionality.fns[k].docs) for k in Functionality.fns.keys())
    start = template.format(acc, commands)
    if len(special) > 0:
        return start + "\nMore specifically:\n" + special
    return start

browser = sakai.SakaiBrowser()

def parse_args(argv):
    rv = ''
    i = 1
    while i < len(argv):
        curr = argv[i]
        mlm, confidence = most_likely_match(argv[i], Functionality.fns.keys())
        if confidence == 3:
            return usage(rv, "Could not parse {}".format(argv[i]))

        j = i
        while j < len(argv) and most_likely_match(argv[j], ["then", "--then"])[1] > 2:
            j += 1
        ok, v = Functionality.fns[mlm](*argv[i + 1:j])
        i = j + 1
        if not ok:
            return usage(rv, '{}: {}'.format(mlm, v))
        rv += v + '\n' + '=' * 50 + '\n'
    return rv

@Functionality.add_function({0}, 'todo', 'Outputs a todo list sorted by due dates from sakai')
def todo():
    vals = []
    for course in sakai.list_courses(browser):
        for asst in sakai.find_assignments(browser, course[0]):
            title, date = asst
            date = dp.parse(date)
            if date >= dt.datetime.now():
                vals.append((course, title, date))

    vals = sorted(vals, key = lambda a: a[2])
    return True, "TODO:\n" + '\n'.join("{} for {} due in {}".format(v[1], v[0][1], clean_time(v[2])) for v in vals)

@Functionality.add_function({0}, 'courses', 'Outputs the list of starred courses in Sakai')
def courses():
    return True, "COURSES:\n" + '\n'.join(course[1] for course in sakai.list_courses(browser))

if __name__ == "__main__":
    import sys
    pv = parse_args(sys.argv)
    browser.close()
    print(pv)
