# fquery
Functional Query Language, with a interpreter, written in python 3.10.

## Language Design/Ethos.

The language was designed to reduce the complexity of writing database
code and to force functional design paradigms when dealing with datasets.
The reason behind this choice was to improve efficiency. 

## Planned Features:
- builtins written as much as possible in the language itself
- Lazily evaluated tables
- streams
- Piping
- self-optimzing streams
- events (requests) for exposing query results

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
