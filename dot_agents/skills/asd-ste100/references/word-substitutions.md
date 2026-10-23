# Word substitutions

An illustrative list, not the dictionary. ASD-STE100 approves about 900 words. This file cannot
replace Part 2 of the standard. Use it to remove the most frequent errors in software text.

Rules that apply: 1.1, 1.2, 1.3, 1.11, 3.7, 9.2, 9.3, 9.4.

## The one that matters most

`make sure` is the approved verb. These are all unapproved: `verify`, `check` (as a verb),
`confirm`, `ensure`, `validate`, `assert`.

`check` is approved as a noun only. Write `do a check of the log file`.

## Verbs

| Do not use | Use |
| --- | --- |
| accomplish, achieve, carry out, execute, perform | do |
| acquire, obtain, procure | get |
| attempt | try |
| commence, initiate | start |
| terminate, halt, cease | stop |
| utilize, employ, leverage | use |
| require | need, or `you must` |
| permit, enable | let, or `you can` |
| indicate | show |
| identify | find |
| determine | find, or decide |
| modify, alter, adjust | change |
| remove, eliminate, delete | remove (select one and keep it) |
| install, deploy, provision | install (select one and keep it) |
| verify, validate, confirm, ensure | make sure |
| examine, inspect, review | inspect (select one and keep it) |
| illustrate, demonstrate | show |
| retain | keep |
| transmit, forward | send |
| receive | get |
| construct, generate, produce | make, or build |
| comprise, constitute | hold, or contain |
| observe | look at, or see |
| follow (to mean obey) | obey |

`to follow` means `to come after`. Write `Obey the safety instructions`.

## Nouns and adjectives

| Do not use | Use |
| --- | --- |
| assistance | help |
| commencement | start |
| requirement | need |
| modification | change |
| utilization | use |
| approximately | about |
| adequate, sufficient | enough |
| additional | more |
| numerous, multiple | many |
| initial | first |
| final, ultimate | last |
| subsequent | next |
| prior | earlier |
| optimum, optimal | best |
| erroneous | incorrect |
| operational, functional | serviceable, or `it operates` |
| capability, functionality | function |
| methodology | method |
| in the vicinity of | near |

## Connecting words and phrases

| Do not use | Use |
| --- | --- |
| however, nevertheless, nonetheless | but (or write two sentences) |
| therefore, consequently, thus, hence | therefore (select one and keep it) |
| additionally, furthermore, moreover | also |
| prior to | before |
| subsequent to, following | after |
| in order to | to |
| due to the fact that, owing to the fact that | because |
| in the event that | if |
| with regard to, regarding, concerning | about |
| in conjunction with | with |
| via, by means of | with, or by |
| per | for each |
| whilst | while |
| currently, presently, at this time | now |
| approximately | about |

## Phrasal verbs (rule 9.3)

A phrasal verb is a verb with a preposition. Its meaning is not clear from its parts.

| Do not use | Use |
| --- | --- |
| set up | install, configure, or start |
| put together | assemble |
| take off | remove |
| put in | install |
| turn on | energize, or start |
| turn off | de-energize, or stop |
| find out | find, or learn |
| carry out | do |
| go through | read, or examine |
| bring up | start, or display |
| shut down | stop |
| back up | make a backup |
| roll out | release |
| roll back | restore |
| spin up | start |
| tear down | remove |
| look into | examine |
| come up with | make, or select |
| figure out | find, or solve |

## Latin abbreviations (GR-6)

| Do not use | Use |
| --- | --- |
| e.g. | for example |
| i.e. | that is |
| etc. | write the complete list |
| vs. | compared to |
| N.B. | note |
| et al. | and other persons |

## Software terms to keep

These are technical nouns under rules 1.5 and 1.6. Do not translate them into simpler English. Keep
the exact form.

- Names of products, services, and companies
- Names of functions, variables, files, and directories
- Command names, flags, and error strings
- Protocol and format names, for example `HTTP`, `JSON`, `YAML`
- Identifiers, for example an ARN, a route ID, or a table name

Rule 1.11 applies to them: use one name for one thing. Do not write `the connect handler` on one
page and `the connection function` on the next page.

## How to select a term for your project

Rules 1.8, 1.9, and 1.11 give you the method:

1. Make a list of the things that your text describes.
2. Select one short name for each thing.
3. Write the unapproved alternatives beside each name.
4. Put the list in the repository.
5. Use only the names in the list.
