# Contributing to Pax-Academia

## Non Contributors

If you are not listed as a contributor, you are still welcome to help out!
Please fork the repository and make a pull request with your changes.
Follow the guidelines below to ensure your pull request correct. Incorrect pull requests will be rejected.

## Contributors

Please create your own branch and make a pull request to the master branch.
Follow the guidelines below to ensure your pull request correct. Incorrect pull requests will be rejected.

## PR Guidelines

### Branch Names

Please name your branch as follows:
`<your-name>.<feature-name>`

### Commit Messages/ commits

- Use the present tense ("Add feature" not "Added feature")
- Keep messages short and concise
- Keep commits small and concise (commit regularly)

### Pull Requests

#### Title

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

#### Description

Your description is where you can go into more detail about your changes.
Please include _at least_ the following:
- What you changed
- Why you changed it

If your PR is related to an issue, please include the issue number in the description.
If it solves the issue, please include `Closes #<issue-number>` in the description. This will automatically close the issue when the PR is merged.

#### Labels

Each PR MUST have at least one label. The following labels are available:
- `bugfix` (bug fix) => PR's with this label must have a corresponding issue
- `enhancement` (existing feature)
- `documentation` (documentation)
- `dependencies` (Updates a dependency) 
- `feature` (new feature) 
- `hotfix` (very small bugfix/typo fix)

(PR's with no label will be rejected)


## Code Guidelines