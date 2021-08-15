# git repos of SVG images [<img alt="git Logo" src="https://www.vectorlogo.zone/logos/git-scm/git-scm-icon.svg" height="80" align="right" />](https://logosear.ch/)

[![build](https://github.com/VectorLogoZone/git-svg-icons/actions/workflows/release.yaml/badge.svg)](https://github.com/VectorLogoZone/git-svg-icons/actions/workflows/release.yaml)
[![quality](https://github.com/VectorLogoZone/git-svg-icons/actions/workflows/quality.yaml/badge.svg)](https://github.com/VectorLogoZone/git-svg-icons/actions/workflows/quality.yaml)

## Icons

Public git repositories of SVG icons: this is the list used by [IconSear.ch](https://iconsear.ch/).

You can see a nicely formatted version of the list at [IconSear.ch](https://iconsear.ch/sources/index.html).

The [raw list data](data/icons.yaml) is here in this repository.

## Logos

Public git repositories of SVG logos: this is the list used by [LogoSear.ch](https://logosear.ch/).

You can see a nicely formatted version of the list at [LogoSear.ch](https://logosear.ch/sources/index.html).

The [raw list data](data/logos.yaml) is here in this repository.

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
