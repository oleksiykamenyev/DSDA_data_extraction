`integer` **tics**, converted from `[hh:]mm:ss[.tt]`  
`integer` **tas**
```ruby
0: Not Tas, 1: Segmented, 2: Slowdown, 3: Partial Building, 4: Built
```
`integer` **guys**, number of players *in the game*  
`string` **level** *`Map 01, E1M1, Ep1, D2ALL`*  
`text` **levelstat** *`02:11.13,04:01.00`*  
`datetime` **recorded_at**  
`boolean` **has_tics**  
`string` **engine** *`PRBoom+ v2.5.1.4 cl9\nXDRE 2.14`*  
`belongs_to` **wad**  
`belongs_to` **category**  
`has_many` **players**  
`has_many` **tags**  