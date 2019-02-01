from functools import wraps

import dateparser as dp

import sakai
from util import most_likely_match

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
        Functionality.fns[name] = self
    def __call__(self, *args):
        if len(args) not in self.args:
            return False, self.docs
        return True, self.function(*args)
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

    commands = '\n'.join(n.name for n in Functionality.fns.keys())
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
        i = j
        ok, v = Functionality.fns[mlm](argv[i:j])
        if not ok:
            return usage(rv, '{}: {}'.format(mlm, v))
        rv += v + '\n'
    return rv

@Functionality.add_function({0}, 'todo', 'Returns the todo list sorted by due dates from sakai')
def todo():
    vals = []
    for course in list_courses(browser):
        for asst in find_assignments(browser, course[0]):
            title, date = asst
            date = dp.parse(date)
            vals.append((course, title, date))

    vals = sorted(vals, key = lambda a: a[1])
    return '\n'.join("{} for {} due on {}".format(v[1], v[0], v[2].strftime('%m/%d/%y')) for v in vals)

if __name__ == "__main__":
    import sys
    pv = parse_args(sys.argv)
    browser.close()
    print(pv)
