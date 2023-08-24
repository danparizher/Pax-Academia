# Contributing to Pax-Academia

Pax Academia is an open source project, and we welcome contributions of all kinds from anyone. As this project has grown to become a large project, we have had to implement some guidelines to ensure that the project remains maintainable and that contributions are of high quality, since this bot is used by well over 150.000 people.

This document outlines the process for contributing to the project. Please read it carefully before making a contribution so that you know what to expect and what is expected of you.

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
- `refactor` (refactoring production code)

(PR's with no label will be rejected)

#### 3.3.4 Content
A PR may not contain code and commits not related to the issue it is solving or feature it is completing.
F.ex. 
- a PR solving issue #1 may not contain code or commits related to issue #2.
- Do not include a commit that changes something in the docs when working on a discord command (unless the docs are related to the command)
- Do not refacter code in cog A when working on cog B
- ...


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
@sebastiaan-daniels must review external libraries for security vulnerabilities before they can be used.


## 5. Reviewing Guidelines

### 5.1 Code Reviews from contributors

Each contributor, regardless of their role, is allowed to review code.
However, requested changes or comments made by contributors do not have to be followed by the author of the PR. They are merely suggestions.

### 5.2 Code Reviews from maintainers (Code Owners)

#### 5.2.1 General
Each PR, depending on its complexity, must be reviewed by at least n maintainers. (see 5.2.3 for the number of maintainers required for each type of PR)
No code may be merged without the approval of those code owners. All code owners must be requested to review the PR. (this should be done automatically by github)

#### 5.2.2 Code Owners
The project maintainers (owners), are the people listed under `.github/CODEOWNERS`.

#### 5.2.3 Reviewing
For each type of PR, the following amount of code owners must approve the PR before merging:
- `hotfix` => 1
- `documentation` => 1
- `dependencies` => 1 + @sebastiaan-daniels
- `bugfix` => 2
- `enhancement` => 3
- `refactor` => 3
- `feature` => 4

#### 5.2.4 Accepted code
If the required number of code owners have approved the PR, the PR may be merged by any code owner.

#### 5.2.5 Changes requested by a code owner
If any code owner requests changes, (regardless whether or not the required number of code owners have approved the PR), the PR may not be merged until those changes have been either made or discussed and agreed upon.

The code owner that requested changes must re-review the PR and approve it before it can be merged.

### 5.3 PR's from code owners

#### 5.3.1 General
If a code owner makes a PR, the same rules apply as for any other contributor. The PR must be reviewed by the required number of code owners, and may not be merged until the required number of code owners have approved the PR.

#### 5.3.2 Special cases

Since a user cannot review their own PR, there are some cases in which more code owners must review the PR than there are existing.
In these cases, if all code owners have approved the PR, the PR may be merged by any code owner.
I.e if a code owner creates a feature, only 3 code owners must add a review. (since there are only 4 owners.)