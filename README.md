# RA.Connect

RA.Connect is a web application designed to streamline University of Virginia dorm residents to their resident advisors (RAs). The project was a semester-long group [assignment](https://s24.cs3240.org/project.html#project-overview) for CS 3240 (Advanced Software Development Techniques) and should **not** be used for serious reports.

## Installation

First, clone the repository on your local machine:

```bash
git clone <repo_link.git>
```

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the dependencies listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

The following inputs (in presented order) are necessary to initialize and configure your local SQLite database:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Usage

Run the following commands to launch the web app to the localhost IP address [http://127.0.0.1:8000/](http://127.0.0.1:8000/):

```bash
python manage.py runserver
```

## Group

The project was designed and built in a group effort of four members:

- Yanson Khuu, DevOps Manager (fbx2jt)
- Kaitlyn Kreth, Requirements Manager (qte7kg)
- Megan Lewis, Testing Manager (nxk7tq)
- Hugo Abbot, Software Architect (drt3sm)

Additional information on the positions and the respective responsibilities can be viewed on the project details [page](https://s24.cs3240.org/project.html#team-roles).

## License

[MIT](https://choosealicense.com/licenses/mit/)
