# fquery
Functional Query Language, with a interpreter, written in python 3.10.

## Language Design/Ethos.

The language was designed to reduce the complexity of writing database
code and to force functional design paradigms when dealing with datasets.
The reason behind this choice was to improve efficiency. 
## Inspiration.

Within the first few weeks of classes for Database 1, I had noticed how 
antiquated the design features of SQL was, and how chained calls become
complex and disgusting quickly. Combine that with my knowledge of
functional design paradigms, it made sens to me, to make a functional
query language, with completely lazy values, allowing for dynamic 
tables, functions, and piping.

## Planned Features:
- builtins written as much as possible is in the fquery itself
- Lazily evaluated tables
- streams
- Piping
- self-optimzing streams
- events (requests) for exposing query results

## Planned Timeline
- [ ] exec working
  - [x] Variables
  - [x] Lambdas
  - [x] Output
  - [x] Recursion
  - [x] Piping
  - [x] Database Loading
  - [ ] Database Updating
  - [ ] Database Deletion
  - [ ] Database Creation
  - [ ] Input
  - [ ] Iterator base type
  - [ ] List base type
  - [ ] Named Tuple base type
  - [ ] Maps
  - [ ] Filter
  - [ ] Reduce
  - [ ] Namespaces
  - [ ] Imports
  - [ ] Events
  - [ ] Exceptions
  - [ ] Optimizations
- [ ] Make a Minimum Viable Parser.
  - [ ] Token generation
  - [ ] Pre-calculating results
  - [ ] Error Reporting
- [ ] Additional Features.
  - [ ] Adding Table Visualization
  - [ ] Exporting to CSV's
  - [ ] Storing lambdas in `.ftab`'s
  

## Language spec:

The language is designed to be simple to read, and write. As such,
many operators are available for you to use

```
:=      : assignment, eager evaluation
?=      : assignment, lazy evaluation
=>      : lambdas
.       : member operator.
*       : depack, or multiply
/       : divide
...
map     : map operator
filter  : filter operator
reduce  : reduction operation
@event  : event wrapper, whatever is provided is required
          to make the event fire.
|>      : Pipe operator
```
