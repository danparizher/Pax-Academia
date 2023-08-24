# Contributing to Pax-Academia

## 1. Non Contributors

If you are not listed as a contributor, you are still welcome to help out!
Please fork the repository and make a pull request with your changes.
Follow the guidelines below to ensure your pull request correct. Incorrect pull requests will be rejected.

## 2. Contributors

Please create your own branch and make a pull request to the master branch.
Follow the guidelines below to ensure your pull request correct. Incorrect pull requests will be rejected.

## 3. PR Guidelines

### 3.1 Branch Names

Please name your branch as follows:
`<your-name>.<feature-name>`

### 3.2 Commit Messages/ commits

- Use the present tense ("Add feature" not "Added feature")
- Keep messages short and concise
- Keep commits small and concise (commit regularly)

### 3.3 Pull Requests

#### 3.3.1 Title
Your title should be short and concise. It should be in the format:
`<type>: <desc>`
where `<type>` is one of the following:
- `feat` (feature)
- `fix` (bug fix)
- `docs` (documentation)
- `style` (formatting, missing semi colons, etc; no code change)
- `refactor` (refactoring production code)
- `test` (adding missing tests, refactoring tests; no production code change)
- `chore` (updating grunt tasks etc; no production code change)

and `<desc>` is a short description of the changes made.

#### 3.3.2 Description
Your description is where you can go into more detail about your changes.
Please include _at least_ the following:
- What you changed
- Why you changed it

If your PR is related to an issue, please include the issue number in the description.
If it solves the issue, please include `Closes #<issue-number>` in the description. This will automatically close the issue when the PR is merged.

#### 3.3.3 Labels
Each PR MUST have at least one label. The following labels are available:
- `bugfix` (bug fix) => PR's with this label must have a corresponding issue
- `enhancement` (existing feature)
- `documentation` (documentation)
- `dependencies` (Updates a dependency) 
- `feature` (new feature) 
- `hotfix` (very small bugfix/typo fix)

(PR's with no label will be rejected)


## 4. Code Guidelines

### 4.1 PEP8

Please follow the PEP8 style guide. To do so, please use the [black](https://pypi.org/project/black/) python formatter.
(All code in this repository is formatted using black)

### 4.2 Documentation

#### 4.2.1 Docstrings
Please include docstrings for all functions and classes. These do not have to be long,
but at least include the basic information (what the function does, what the parameters are, what the return value is, etc).

#### 4.2.2 Comments
Please include comments where necessary. This includes:
- Comments explaining complex code
- Comments explaining why you did something a certain way

#### 4.2.3 Type Hints
Please include type hints for all functions and classes.

### 4.3 Complexity

Please keep your code as simple as possible. We prefer longer, simpler code over shorter, more complex code.
Avoid long list comprehensions, complex lambda functions, etc.

### 4.4 Imports

Please keep your imports as simple as possible. Avoid importing entire modules, and avoid importing multiple modules on one line.

[!IMPORTANT]
If you wish to use an external library, please ask first. We want to keep the number of external libraries to a minimum.
(using external libraries already included in the requirements.txt is fine).

[!WARNING]
@skagame must review external libraries for security vulnerabilities before they can be used.


## 5. Reviewing Guidelines