# git repos of SVG images [<img alt="git Logo" src="https://www.vectorlogo.zone/logos/git-scm/git-scm-icon.svg" height="80" align="right" />](https://logosear.ch/)

[![build](https://github.com/VectorLogoZone/git-svg-icons/actions/workflows/release.yaml/badge.svg)](https://github.com/VectorLogoZone/git-svg-icons/actions/workflows/release.yaml)
[![quality](https://github.com/VectorLogoZone/git-svg-icons/actions/workflows/quality.yaml/badge.svg)](https://github.com/VectorLogoZone/git-svg-icons/actions/workflows/quality.yaml)

These are the lists of public git repositories of SVG images used by [LogoSearch](https://logosear.ch/) and [IconSearch](https://iconsear.ch/).

The [raw list for icons](data/iconsearch.yaml) and the [raw list for logos](data/logosearch.yaml) are here in this repository.

You can see a nicely formatted version of the lists at [LogoSearch](https://logosear.ch/sources/index.html) and [IconSearch](https://iconsear.ch/sources/index.html).


## Contributing

[Yes please!](CONTRIBUTING.md)

## License

[CC0](LICENSE.txt)

## Credits

[![Bash](https://www.vectorlogo.zone/logos/gnu_bash/gnu_bash-ar21.svg)](https://www.gnu.org/software/bash/ "Scripting")
[![Git](https://www.vectorlogo.zone/logos/git-scm/git-scm-ar21.svg)](https://git-scm.com/ "Version control")
[![Github](https://www.vectorlogo.zone/logos/github/github-ar21.svg)](https://github.com/ "Git Repositories")
[![Gitlab](https://www.vectorlogo.zone/logos/gitlab/gitlab-ar21.svg)](https://about.gitlab.com/ "Git Repositories")
[![Python](https://www.vectorlogo.zone/logos/python/python-ar21.svg)](https://www.python.org/ "data load script")
[![YAML](https://www.vectorlogo.zone/logos/yaml/yaml-ar21.svg)](http://yaml.org/ "list storage")

## Running

Generally:

```bash
pip3 install sh unidecode pyaml
bin/loadrepo.py
```

For the specific parameters used in production, see the [Github Action](.github/workflows/release.yaml).

## To Do

- [ ] validate_repo: make sleep into an argument
- [ ] validate_repo: support github auth to avoid "too many requests" when running from GHA without sleeping
- [ ] release description should include the count of repos and images
