# .gitignore Generation via Toptal gitignore API

Use this reference when the user asks to review, generate, or fix a `.gitignore`. The Toptal gitignore API provides community-maintained templates — treat them as **starting material, not final output**. The actual `.gitignore` must reflect this project's actual stack and conventions.

## API behavior

Base URL: `https://www.toptal.com/developers/gitignore/api/`

| Endpoint | Purpose | Format |
|---|---|---|
| `/api/list` | Comma-delimited list of every supported template name | `text/plain` |
| `/api/<t1,t2,…>` | Returns a `.gitignore` body composed of all named templates, concatenated with `### <Name> ###` section headers and a `# Created by …` comment block | `text/plain` |

- **Comma-delimited, no spaces.** `/api/node,python` is valid; `/api/node, python` is not.
- **Order is preserved** in the output. Put OS / editor templates first so they don't get overridden by later patterns.
- **Forgiving on partial invalidity.** A single unknown name does *not* abort the call — the valid templates are still emitted and the unknown one is surfaced as a `#!! ERROR: <name> is undefined. Use list command to see defined gitignore types !!#` comment. Verify the response body contains only `### <Name> ###` sections for the templates you requested.
- **HEAD is blocked.** `curl -I` returns HTTP 403. Use GET only.
- **Referer header is required by some CDNs.** Prefer `webfetch` / `firecrawl_scrape` / `curl -s` over `curl -I`. If the response is empty, add a `Referer: https://www.toptal.com/developers/gitignore` header (or retry with `webfetch`).

Fetch the list once per session with `webfetch` and cache the names in this file (already pre-seeded below). Fetch individual templates only when needed.

## Pre-seeded template catalog

Names are grouped by role. This is a curated subset of the full `/api/list` for fast lookup — the full list is reproduced at the bottom of this file as a fallback. If a name is missing here, check the full list or hit `/api/list`.

### Operating systems
`macos`, `osx` *(alias for macos)*, `windows`, `linux`

### Editors and IDEs
`visualstudiocode`, `jetbrains` *(umbrella for all JetBrains IDEs)*, `intellij`, `intellij+all`, `intellij+iml`, `pycharm`, `pycharm+all`, `pycharm+iml`, `webstorm`, `webstorm+all`, `webstorm+iml`, `phpstorm`, `phpstorm+all`, `phpstorm+iml`, `rubymine`, `rubymine+all`, `rubymine+iml`, `goland`, `goland+all`, `goland+iml`, `clion`, `clion+all`, `clion+iml`, `rider`, `appcode`, `appcode+all`, `appcode+iml`, `androidstudio`, `eclipse`, `netbeans`, `sublimetext`, `vim`, `emacs`, `xcode`, `xcodeinjection`, `notepadpp`, `atom` *(deprecated but still in list)*, `nova`, `textmate`

### Languages and runtimes
`node`, `python`, `pythonvanilla`, `go`, `rust`, `java`, `kotlin`, `scala`, `groovy`, `clojure`, `ruby`, `php`, `c`, `c++`, `csharp`, `dotnetcore`, `aspnetcore`, `fsharp`, `swift`, `objective-c`, `dart`, `flutter`, `elixir`, `erlang`, `haskell`, `scala`, `lua`, `perl`, `r`, `julia`, `crystal`, `nim`, `zig`, `ocaml`, `fsharp`, `fortran`, `pascal` *(via `delphi`, `lazarus`, `freepascal`)*, `cobol` *(not in list)*

### Frontend frameworks and tooling
`react`, `reactnative`, `nextjs`, `nuxtjs`, `vuejs`, `vue`, `angular`, `svelte`, `astro`, `gatsby`, `docusaurus`, `remix`, `remix+arc`, `remix+cloudflarepages`, `remix+cloudflareworkers`, `remix+netlify`, `remix+vercel`, `storybookjs`, `cypressio`, `jupyternotebooks`, `ionic3`, `nwjs`, `cordova`, `electron` *(not in list — covered by `node`)*

### Backend frameworks
`django`, `flask`, `laravel`, `rails`, `symfony`, `phoenix`, `spring` *(not in list — use `java`)*, `dotnetcore`, `aspnetcore`, `express` *(not in list — covered by `node`)*, `fastapi` *(not in list — covered by `python`)*, `actix` *(not in list — covered by `rust`)*, `gin` *(not in list — covered by `go`)*

### Build tools and package managers
`composer`, `bower`, `yarn`, `maven`, `gradle`, `sbt`, `leinigen` *(not in list — use `leiningen`)*, `leiningen`, `bazel`, `cmake`, `make` *(not in list — use `c`/`c++`)*, `conan`, `vcpkg`, `pdm` *(covered by `python` patch)*, `poetry` *(covered by `python` patch)*, `pipenv` *(covered by `python`)*, `pnpm` *(not in list — covered by `node`)*

### Cloud / infra
`terraform`, `terragrunt`, `pulumi`, `pulumi+stacks`, `ansible`, `ansibletower`, `chefcookbook`, `puppet`, `puppet-librarian`, `docker` *(not in list — generic patterns are usually added manually)*, `kubernetes` *(not in list)*, `serverless`, `vercel`, `netlify` *(via `vercel`)*

### Common utility templates (rarely needed, available if asked)
`archives`, `compressed`, `compressedarchive`, `backup`, `diskimage`, `ssh`, `dotfilessh`, `env`, `venv`, `virtualenv`, `patch`, `diff`, `logs` *(not in list)*, `database`, `certificates`, `secrets` *(not in list — handle manually)*, `tags`, `text`

### Patch suffixes
Templates suffixed `+all`, `+iml`, `+strict` add the IDE's "all files" or "iml files" mode. `appcode`, `clion`, `goland`, `intellij`, `phpstorm`, `pycharm`, `rubymine`, `webstorm`, `jetbrains` all support these.

## Workflow

When asked to create, fix, or review a `.gitignore`:

1. **Read the current `.gitignore`** if one exists. Note what is already covered so the agent doesn't propose duplicates or contradict established rules. Honor any project-specific conventions (e.g. team-policy ignores for `.env*`, license headers).
2. **Identify the stack** from executable sources of truth, in priority order:
   - Root manifests: `package.json`, `pnpm-lock.yaml`, `Cargo.toml`, `go.mod`, `requirements.txt` / `pyproject.toml` / `Pipfile`, `Gemfile`, `composer.json`, `pom.xml`, `build.gradle*`, `*.csproj`
   - Tooling configs: `.nvmrc`, `.python-version`, `.tool-versions`, `.ruby-version`, `.rust-toolchain`, `tsconfig.json`, `vite.config.*`, `next.config.*`
   - CI: `.github/workflows/*.yml`, `.gitlab-ci.yml`
   - Existing IDE dirs at root: `.vscode/`, `.idea/`, `*.iml`
3. **Map stack → template names** using the catalog above. Choose at most one OS template (match the dominant dev machine), one or more editor templates, one language/runtime template, and one or more framework templates.
4. **Fetch** each chosen template via `webfetch` against `https://www.toptal.com/developers/gitignore/api/<comma-list>`. Use a single comma-delimited call to avoid round-trips.
5. **Verify** the response. Reject any template whose response contains `#!! ERROR:`. If an error appears, drop that template and re-fetch with the remaining valid names.
6. **Compose** the new `.gitignore`:
   - Header comment naming the project (one line, optional).
   - OS section first (always — patterns like `.DS_Store` should not be overridden).
   - Editor/IDE section.
   - Language/runtime section.
   - Framework/build section.
   - **Project-specific entries** last. These come from inspecting the actual project, not from the API: lockfile decisions, monorepo workspace globs, generated dirs, vendored deps, environment files, IDE config the team does/doesn't commit, large data files.
   - The Toptal `# Created by …` / `# End of …` banner comments are optional; remove them if the team prefers a clean file.
7. **De-duplicate and reconcile**:
   - If a project-specific entry overlaps an API entry (e.g. both ignore `/dist`), keep one.
   - If the API ignores something the project *commits* intentionally (e.g. a tracked `dist/` for a static-site repo), strip the conflicting pattern.
   - If the API is silent on something obvious in the project (lockfile, generated client, monorepo outputs), add it manually and mark with a short `# project-specific` comment.
8. **Validate**: `git check-ignore -v <candidate-path>` for any non-obvious entry, against actual project files, before committing.
9. **Show diff** to the user and ask before writing, unless the user explicitly said "create" / "fix" without preview.

## What NOT to do

- **Don't paste the API body verbatim.** It is a *reference*, not the final file. The API bundles too much (every framework, every patch, every commented-out option). A real `.gitignore` should be tight and project-specific.
- **Don't fetch every plausible template.** Two to five templates is the typical sweet spot. More means more noise.
- **Don't ignore the current `.gitignore`.** It often encodes team policy (e.g. which `.env*` to allow, which IDE files to commit). Preserve it unless the user says otherwise.
- **Don't add patterns "just in case".** Every line costs a `git status` scan on every file. Keep the file under ~50 lines for most repos; past ~80 lines it stops being a checklist and becomes noise.
- **Don't commit secrets or `.env`.** The API templates cover this, but verify — `python` and `node` ignore `.env` while `dotnetcore` does not. Always end with an explicit `.env*` / `!.env.example` block unless the project intentionally commits env files.

## Quick command snippets

Fetch one template (preview):
```
webfetch https://www.toptal.com/developers/gitignore/api/node
```

Fetch several at once:
```
webfetch https://www.toptal.com/developers/gitignore/api/macos,visualstudiocode,node,nextjs
```

Refresh the full template list (only when the catalog below looks stale or missing a name):
```
webfetch https://www.toptal.com/developers/gitignore/api/list
```

## Full template list (verbatim from `/api/list`)

Use this when the curated catalog above is missing a name. Last refreshed: 2026-07-12.

```
1c,1c-bitrix,a-frame,actionscript,ada
adobe,advancedinstaller,adventuregamestudio,agda,al
alteraquartusii,altium,amplify,android,androidstudio
angular,anjuta,ansible,ansibletower,apachecordova
apachehadoop,appbuilder,appceleratortitanium,appcode,appcode+all
appcode+iml,appengine,aptanastudio,arcanist,archive
archives,archlinuxpackages,asdf,aspnetcore,assembler
astro,ate,atmelstudio,ats,audio
autohotkey,automationstudio,autotools,autotools+strict,awr
azurefunctions,azurite,backup,ballerina,basercms
basic,batch,bazaar,bazel,bitrise
bitrix,bittorrent,blackbox,blender,bloop
bluej,bookdown,bower,bricxcc,buck
c,c++,cake,cakephp,cakephp2
cakephp3,calabash,carthage,certificates,ceylon
cfwheels,chefcookbook,chocolatey,circuitpython,clean
clion,clion+all,clion+iml,clojure,cloud9
cmake,cocoapods,cocos2dx,cocoscreator,codeblocks
codecomposerstudio,codeigniter,codeio,codekit,codesniffer
coffeescript,commonlisp,compodoc,composer,compressed
compressedarchive,compression,conan,concrete5,coq
cordova,craftcms,crashlytics,crbasic,crossbar
crystal,cs-cart,csharp,cuda,cvs
cypressio,d,dart,darteditor,data
database,datarecovery,dbeaver,dbt,defold
delphi,deno,dframe,diff,direnv
diskimage,django,dm,docfx,docpress
docusaurus,docz,dotenv,dotfilessh,dotnetcore
dotsettings,doxygen,dreamweaver,dropbox,drupal
drupal7,drupal8,e2studio,eagle,easybook
eclipse,eiffelstudio,elasticbeanstalk,elisp,elixir
elm,emacs,ember,ensime,episerver
erlang,espresso,executable,exercism,expressionengine
extjs,fancy,fastlane,finale,firebase
fish,flashbuilder,flask,flatpak,flex
flexbuilder,floobits,flutter,font,fontforge
forcedotcom,forgegradle,fortran,freecad,freepascal
fsharp,fuelphp,fusetools,games,gatsby
gcov,genero4gl,geth,ggts,gis
git,gitbook,go,godot,goland
goland+all,goland+iml,goodsync,gpg,gradle
grails,greenfoot,groovy,grunt,gwt
haskell,helm,hexo,hol,homeassistant
homebrew,hsp,hugo,hyperledgercomposer,iar
iar_ewarm,iarembeddedworkbench,idapro,idris,igorpro
images,infer,inforcms,inforcrm,intellij
intellij+all,intellij+iml,ionic3,jabref,janet
java,jboss,jboss-4-2-3-ga,jboss-6-x,jboss4
jboss6,jdeveloper,jekyll,jenv,jetbrains
jetbrains+all,jetbrains+iml,jgiven,jigsaw,jmeter
joe,joomla,jsonnet,jspm,julia
jupyternotebooks,justcode,kaldi,kate,kdevelop4
kdiff3,keil,kentico,keystonejs,kicad
kirby2,kirby3,kobalt,kohana,komodoedit
konyvisualizer,kotlin,labview,labviewnxg,lamp
laravel,latex,lazarus,leiningen,lemonstand
less,liberosoc,librarian-chef,libreoffice,lighthouseci
lilypond,linux,lithium,localstack,logtalk
lsspice,ltspice,lua,lyx,macos
magento,magento1,magento2,magic-xpa,matlab
maven,mavensmate,mdbook,mean,mercurial
mercury,meson,metals,metalsmith,metaprogrammingsystem
meteor,meteorjs,microsoftoffice,mikroc,mill
moban,modelsim,modx,momentics,monodevelop
mplabx,mule,nanoc,nativescript,ncrunch
nesc,netbeans,nette,nextjs,nikola
nim,ninja,node,nodechakratimetraveldebug,nohup
notepadpp,nova,now,nuxtjs,nwjs
objective-c,obsidian,ocaml,octave,octobercms
opa,opencart,opencv,openfoam,openframeworks
openframeworks+visualstudio,oracleforms,orcad,osx,otto
oxideshop,oxygenxmleditor,packer,pants,particle
patch,pawn,perl,perl6,ph7cms
phalcon,phoenix,php-cs-fixer,phpcodesniffer,phpstorm
phpstorm+all,phpstorm+iml,phpunit,pico8,pimcore
pimcore4,pimcore5,pinegrow,platformio,playframework
plone,polymer,powershell,premake-gmake,prepros
prestashop,processing,progressabl,psoccreator,pulumi
pulumi+stacks,puppet,puppet-librarian,purebasic,purescript
putty,pvs,pycharm,pycharm+all,pycharm+iml
pydev,python,pythonvanilla,qml,qooxdoo
qt,qtcreator,r,racket,rails
react,reactnative,reasonml,red,redcar
redis,remix,remix+arc,remix+cloudflarepages,remix+cloudflareworkers
remix+netlify,remix+vercel,renpy,replit,retool
rhodesrhomobile,rider,robotframework,root,ros
ros2,ruby,rubymine,rubymine+all,rubymine+iml
rust,rust-analyzer,salesforce,salesforcedx,sam
sam+config,sas,sass,sbt,scala
scheme,scons,scrivener,sdcc,seamgen
senchatouch,serverless,shopware,silverstripe,sketchup
slickedit,smalltalk,snap,snapcraft,snyk
solidity,soliditytruffle,sonar,sonarqube,sourcepawn
spark,specflow,splunk,spreadsheet,ssh
standardml,stata,stdlib,stella,stellar
storybookjs,strapi,stylus,sublimetext,sugarcrm
svelte,svn,swift,swiftpackagemanager,swiftpm
symfony,symphonycms,synology,synopsysvcs,tags
tarmainstallmate,terraform,terragrunt,test,testcomplete
testinfra,tex,text,textmate,textpattern
theos-tweak,thinkphp,tla+,toit,tortoisegit
tower,turbo,turbogears2,twincat3,tye
typings,typo3,typo3-composer,umbraco,unity
unrealengine,vaadin,vagrant,valgrind,vapor
vcpkg,venv,vercel,vertx,video
vim,virtualenv,virtuoso,visualbasic,visualstudio
visualstudiocode,vivado,vlab,vrealizeorchestrator,vs
vue,vuejs,vvvv,waf,wakanda
web,webmethods,webstorm,webstorm+all,webstorm+iml
werckercli,windows,wintersmith,wordpress,wyam
xamarinstudio,xcode,xcodeinjection,xilinx,xilinxise
xilinxvivado,xill,xmake,xojo,xtext
y86,yalc,yarn,yeoman,yii
yii2,zendframework,zephir,zig,zsh
zukencr8000
```