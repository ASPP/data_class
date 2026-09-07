# Data class, 2026 Prague notes

- Strong participants
- We finished the class on time

## Data

- I improvised showing how to write a hashmap. The idea was to give the students an intuition of what kind of algorithm 
  is behind the data structures we discussed, to remove the magic from the O(1) retrieval. The demo went well, there
  although there was a bit of confusion on the part about expanding the storage. I committed a new version that should
  be easier to understand. For next time: spend more time on the white board explaining the conflicts and the epxansion
- Remember that the hash function is introduced on Monday (computer architecture), so there's no need to explain it again
- They ask how do they know that something is O(something). Instead of saying "you can look up in the cheatsheet",
  give inyuition: O(N) when you need to look up every item once, O(N^2) you need to compare all pairs, O(log N) when
  you can divide each step by a fraction and don't have to look them all up; O(N log N) -> sorting initially O(N^2) but 
  then people realized you can split in two and sort each piece recursively; etc . Perfect set-up for O(1) demonstration
- Because of the dictionary live coding, I had to cut the "pet shop" show, and everything after it for NumPy

## NumPy
- Use rectangular matrices when using examples with reshape
- Verjinia is going to change the figures to use the same style for memory blocks as in Tiziano's slides

## Tabular
- Need to explain what is tabular data first of all
- The example in the initial exercise is somewhat artificial: have the second table have a location id, city, and country
- Merge command: explain how=left/right/inner
- Messy data slide: it contains many reference to "variables" but we haven't explained what they are (it comes in the
  tidy data slide)
- The explanation of why some data was messy was incorrect in a couple of cases (no one noticed)
