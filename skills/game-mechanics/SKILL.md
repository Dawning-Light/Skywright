---
name: game-mechanics
description: Use when a game project needs its mechanics, systems, or economy written down as structured design data. Not for setting pillars (see `game-pillars`) or rendering a GDD (see `game-gdd`).
---

# Game Mechanics

Conversationally elicits a game's mechanics, systems, and economy from the
owner and writes them as two structured-data shapes into the *consuming game
project's* `design/` directory — never into this repository. This skill is
the schema's root in MDA's sense: mechanics is the only layer a designer
directly authors (dynamics emerge from mechanics in play; aesthetics emerge
from dynamics in a player's experience), so no field anywhere in either shape
below is named for a dynamic or an aesthetic — no `fun`, no `feel`, no
`engagement`. What a mechanic *does* is authorable and goes in the schema;
what playing it *feels like* is an emergent property this schema does not
try to capture.

## Standalone invocation

This skill runs against a project with **no pillars and no comp-analysis
present**. It does not read `design/pillars/*.md`, `design/concept.md`, or
`design/comp-analysis.md`, and does not wait for any of them to exist before
eliciting mechanics. A suggested order exists across the wider six-skill
set — `game-pillars` → `game-comp-analysis` → `game-mechanics` →
`game-tech` → `game-gdd` → `game-critique`, so `game-pillars` before this
skill, and this skill before `game-tech` and `game-gdd` — but it is
suggested, not enforced: nothing here refuses to run for their absence.
`game-tech` reads the mechanic entries and economy graph this skill writes
as trigger data for technical decisions; nothing in either shape changes
for that.

## Process

Before writing or revising any file this skill produces, invoke
`game-authoring` if it has not already run earlier in this conversation. Its
rules govern every body written below.

Elicit conversationally, in whatever order the owner naturally gives it:

1. **Mechanics.** For each mechanic the owner describes, ask enough to fill
   out one mechanic entry (below): what it is, where it sits relative to
   other mechanics already elicited (what it is a *kind of* and what it is a
   *part of*, if either; its children and its parts, if any), one strong
   example of it working as intended, one weak example of it failing or being
   misused.
2. **Systems and economy.** Ask what resources exist, where they enter play,
   where they leave, and what moves or gates them. Map each answer onto a
   node or a connection in the economy graph (below) as it's given, rather
   than collecting free-form notes first and translating them at the end —
   translating late is where a `pool` gets described as a `trader` because
   the distinction blurred in the gap between hearing it and writing it down.

Write each mechanic entry as it is settled, not in a final batch — a mechanic
described early in the conversation and never revisited should already be a
file by the time the conversation ends. Write `design/economy.md` once the
graph stabilizes. Once it exists, change its frontmatter — nodes,
connections, families, a fitted `value_progression` — through
`scripts/economy-tool` (see **Editing the economy graph** below), one
command per change, rather than re-writing the file; its prose sections
stay yours to write.

### Detecting families

**Families are never inferred.** Whenever this skill writes
`design/economy.md`, it detects candidate families — sets of two or more
same-type nodes whose connections are identical apart from their own ids —
and puts each candidate, and its boundary, to the owner. `economy-tool
detect-families` computes both from the file as written — each
candidate's members, and the connections every member has with its own id
abstracted out — skipping nodes already in a family; it prints and never
writes. **This runs on every write, not once**, so a family that emerges
later, as nodes accrete matching connections across sessions the graph was
never touched between, is caught the next time the graph is written rather
than only at the moment it was first authored.

**The boundary is the owner's call, and no signature can make it instead.**
Two node sets with identical edge patterns may still be two families, and
nothing in the edges themselves distinguishes them — a detector that
proposes one merged candidate over both is behaving correctly, not
failing to find a finer signature. Run against the one real graph this
skill has produced, the detector finds three candidates with no false
positives, and merges the seven weapon-proficiency pools with the three
class-proficiency pools, because their edge patterns are genuinely
identical: only the owner knows those are two families, not one. It also
declines to group a fourth pool the file's own prose annotates alongside
those three, because that pool's edge signature differs from theirs — the
detector answers from the edges, not from how the prose already groups
them. Putting the boundary to the owner alongside the candidate is what
lets an owner facing the merged case split it back into two; a proposal
that showed the candidate without it would get this specific case wrong
silently.

A family is written **only where the owner confirms** it: `economy-tool
add-family` for the entry, then one `add-connection` per declaration over
`@<name>` and one `remove-connection` per longhand edge that declaration
replaces, since the file stores a family's declarations, never their
expansion (below). An unconfirmed candidate is **written longhand** — left
as the separate nodes and connections it already was, with no `families`
entry naming them.
Detection puts the candidate and its boundary to the owner and stops
there: propose and confirm, **never infer and write**.

## The mechanic entry

One file per mechanic, at `design/mechanics/<slug>.md` in the consuming
project. This is the Game Ontology Project's own entry shape: a mechanic
named, placed in a taxonomy, described, and illustrated by one example of it
working and one of it failing.

Frontmatter:

- `name` — the slug, matching the filename (without `.md`).
- `title` — the mechanic's Name, as a short phrase.
- `parent` — the `name` of another mechanic entry under `design/mechanics/`,
  or the literal `none`. This is a filename, not free text: a reader (or a
  future renderer) must be able to resolve `parent` by looking for
  `design/mechanics/<parent>.md`, not by matching a description.
- `children` — a list of `name`s of other mechanic entries under
  `design/mechanics/`, possibly empty. Same rule: each entry in the list is a
  filename to resolve, not a description of the child mechanic.
- `part_of` — the `name` of another mechanic entry under `design/mechanics/`,
  or the literal `none`. Same rule as `parent`: this is a filename to
  resolve by looking for `design/mechanics/<part_of>.md`, never prose
  describing a container.
- `parts` — a list of `name`s of other mechanic entries under
  `design/mechanics/`, possibly empty. Same rule as `children`: each entry in
  the list is a filename to resolve, not a description of the part.
- `updated` — the UTC time of the last write to this file, in the
  `YYYY-MM-DDTHH:MMZ` form `game-authoring` defines. Refreshed on every
  write.

Keeping all four relation fields as filenames rather than prose is what makes
the taxonomy walkable: a later skill (or a human) can traverse the whole
mechanics tree by following slugs from file to file, without re-parsing
prose to figure out what points at what.

`parent`/`children` and `part_of`/`parts` are different relations and neither
substitutes for the other. `parent` is **specialization**: a child is a *kind
of* its parent. `part_of` is **composition**: a part is a *piece of* its
container, not a kind of it. A mechanic may carry both — they answer
different questions, and neither constrains the other.

**Modulation gets no field.** A mechanic that changes another's rate, its
cost, or its availability is neither a kind of it nor a part of it, and
forcing that relation into either pair is exactly the error
`game-critique`'s `mechanics-literalist` lens exists to catch. Record it in
one of the two ways the schema already provides — and in both where the
modulation targets an economy node or connection: a `[[mechanic:<slug>]]`
wikilink in this entry's prose, or a `state` connection in
`design/economy.md` — subtype `node-modifier`, `label-modifier`, or
`activator` — targeting the node or connection it modulates.

Body, one heading per field so a reader and a renderer see the same
structure:

- `## Description` — what the mechanic is and how it operates.
- `## Strong example` — one worked case of this mechanic doing what it's for.
- `## Weak example` — one worked case of this mechanic failing, being
  misused, or producing an outcome the design didn't want.
- `## Open Questions` — optional. What about this mechanic is unsettled,
  stated plainly per `game-authoring`, never folded into the description or
  the examples as a hedge. Omit the heading when nothing is open.

A mechanic entry with no `## Weak example` is incomplete: the point of
naming a failure mode is that it's what a later critique pass (see
`game-critique`) checks a design against.

Where any of these sections refers to a fact another record owns — a pillar
it serves, a node or connection in the economy graph, a tech decision that
constrains it — it cites that record with one of the typed wikilinks
`game-authoring` defines (`[[pillar:<slug>]]`, `[[node:<id>]]`,
`[[connection:<id>]]`, `[[tech:<slug>]]`, and the rest) rather than
restating the fact. `parent`, `children`, `part_of`, and `parts` stay bare
slugs in the frontmatter; the wikilink forms are for body prose.

The same rule governs `economy.md`'s prose notes, below. A phrase like "see
`fame`" or "the `quests` mechanic entry" is not that citation — it's a
backtick-wrapped name, which `game-authoring`'s citation rule says
`game-gdd`'s render never parses as a reference, so it neither resolves nor
fails and the debt goes unnoticed until a dedicated sweep finds it, as
happened twice across this project's own history. Reserve backticks in a
prose note for a literal identifier that isn't standing in for a citation —
a node id, a connection id, a YAML field name — and write the citation
itself as `[[mechanic:<slug>]]`, `[[pillar:<slug>]]`, `[[node:<id>]]`, etc.

## The economy graph

One file for the whole graph, at `design/economy.md` in the consuming
project — a Machinations-style node/connection representation of how
resources move through the game.

Frontmatter carries `nodes`, `connections`, the optional `families` block
(below), and one file-level `updated` — the UTC time of the last write to
the file, in the `YYYY-MM-DDTHH:MMZ` form `game-authoring` defines. The one
field covers every node and connection in the file and moves on every
write; `economy-tool` sets it on every change it makes.

Each **node** has:

- `id` — unique within the file.
- `type` — exactly one of `pool`, `source`, `drain`, `gate`, `trader`,
  `converter`. **This set is closed.** A node that doesn't fit one of these
  six is a sign the graph needs two nodes and a connection between them, not
  a seventh type — this schema does not admit one, and a file that invents
  one is wrong rather than merely unconventional.
- **Resource typing.** A `pool`, `source`, `drain`, or `gate` handles exactly
  one resource type, named by its own `id` — a pool holds one, a source or a
  drain moves one, and a gate routes what it receives without changing its
  type, so its type is fixed by its inputs the same way. A node that would
  handle two is two nodes. This is the schema-level statement of the same
  differentiated, non-fungible resource design the research recommends over
  one universal currency, and it is what makes the connection's `resource`
  field (below) conditional rather than universal.
- `value_progression` — optional. An object with fields `{ model,
  coefficients, domain, fit }`, holding a fitted or chosen curve for how this
  node's value changes (for example, a cost-by-level curve). This skill
  declares the field and its four sub-fields; it does not compute them. The
  procedure under **Fitting a value progression** below computes them with a
  companion script, and that fitting math is not part of this file. Until
  that procedure runs, `value_progression` is simply absent from a node that
  hasn't had it computed.

**The state-only node is a modelling error with a stated answer.** A node
that holds a value but that no resource connection ever touches is modelled
as two nodes and a connection, per the closed-set guidance above, rather than
a seventh node type — the closed set of six is faithful to the research it
was adapted from, and this case is not evidence it is short a member.

Each **connection** has:

- `id` — unique within the file, and required. A connection with no `id` is
  invalid, not merely unconventional — it is what makes a connection
  referenceable at all. An **authored** id may not contain `:`, reserved for
  the derived ids a family declaration produces; without that reservation an
  authored id could collide with a derived one in the expanded graph.
- `from` — on a `resource` connection, a node `id`. On a `state` connection,
  a node `id` or `#<connection-id>`.
- `to` — the same rule as `from`.
- `kind` — exactly one of `resource` (this connection moves value from `from`
  to `to`) or `state` (this connection modifies another connection's or
  node's behaviour, rather than moving value itself). **This set is closed**
  the same way node `type` is: a connection that does neither is miscategorized,
  not a sign the set needs a third member.
- `subtype` — optional, and meaningful only on a `state` connection: exactly
  one of `label-modifier`, `node-modifier`, `trigger`, `activator`. **This
  set is closed** on the same terms `type` and `kind` already are: a value
  outside it means the graph is wrong, not that the set needs a fifth member.
  An absent `subtype` means the connection has not been classified yet,
  never a default. A renderer states the absence plainly, on the same terms
  it already states an absent `value_progression` or an absent `rate`. A
  consumer that must act on the value — a simulator — refuses to model that
  connection rather than assuming one. Absence is never read as
  `label-modifier`.
- `rate` — optional. How fast value moves along a `resource` connection.
  `rate` expresses the label-modifier case only: on a `state` connection it
  is how strongly a `label-modifier` connection modifies its target, and it
  carries no general-strength reading across the other three subtypes.
- `resource` — meaningful only on a `resource` connection. A `resource`
  connection whose `from` or `to` is a `trader` or a `converter` carries a
  `resource` naming what moves; elsewhere it is optional. Those two node
  types handle more than one resource type by definition — a trader
  exchanges types, a converter emits a different type than it takes — so
  their edges are the only ones whose content cannot be read off the
  destination. **The partition is exhaustive over the closed set of six**:
  four node types are single-type and need no field, two are not and require
  one, and no node type falls outside both.

**Flow style, one line per connection.** Every entry under `connections` is
written as a single-line flow mapping, so a changed edge is a one-line diff:

```yaml
connections:
  - { id: sale, from: shop, to: gold-pool, kind: resource, resource: gold, rate: 5 }
```

This is a serialization rule over the field set above, not a change to it:
every field a connection carries — `id` and `subtype` included — sits on
that same line, however many of the optional fields a given connection
uses.

**The sigil rule.** `#<id>` names a connection; a bare reference names a
node. Connection ids and node ids are independent namespaces: the same
string may name one of each, and the sigil is what tells them apart. A
reference that resolves to nothing is invalid, not silently skipped.

**`value_progression` is a property of a node, never of a connection, and
`rate` is a property of a connection, never of a node.** A connection records
topology and flow rate — it describes an edge in the graph, and a rate is a
property of that edge. A value series describes how one thing's value
changes over time or over levels, independent of what connects to it — that
is a property of the node itself, not of any one edge touching it. Keeping
them apart matters because a node can have several connections (several
rates) but only one value progression: if `value_progression` lived on a
connection instead, a node with three incoming connections would have no
single place to look for its own value curve, and an editor merging the two
concepts could just as easily attach a flow rate to a node or a value series
to an edge, corrupting both. State this rule here so a later editor sees it
before making that mistake rather than after.

Body: prose notes for context that doesn't belong in the frontmatter (why a
rate is what it is, a balancing concern still open, a design intent behind a
`gate`), organized one subsection per heading. A heading is a node id, a
family name written `## @<name>`, or a member id — nothing else. A heading
that resolves to neither a node id, a family name, nor a member id is
invalid, which is what makes a slash-joined heading, joining two node ids for
one shared paragraph, invalid rather than merely discouraged: it names two
things and resolves to none of the three. When a member has its own section,
a member id keying its own section overrides the family's for that member —
its own notes stand in place of the family's shared ones for that heading,
not beside them.

**Meeting a file that fails this shape.** An economy file can fail the
rules above in four ways: a connection with no `id`; a `from`/`to` reference
with no sigil where one is required; a `state` connection with no `subtype`;
or **block-style edges or slash-joined headings** — a connection written as
a multi-line YAML block instead of the one-line flow mapping, or a heading
joining two node ids for one shared paragraph instead of naming a node id, a
family name, or a member id. Meeting any of these, this skill neither
silently re-writes the file into shape nor refuses to proceed with the write
already under way. It reports which rules the file fails and puts the
upgrade to the owner, on the same propose-and-confirm terms detection
(above) uses for a family: a confirmed upgrade is performed as part of that
same write, and a declined one leaves the file exactly as it is. `game-gdd`
and `game-critique`, which write nothing, report such a file as invalid
rather than rendering it on a best-effort basis. This settles only that the
question is asked; what any particular graph should become stays the owner's
call, and no migration procedure is specified here.

### Families

Frontmatter carries an optional `families` block alongside `nodes` and
`connections`. Each **family** declares a `name`, a node `type`, and a list
of member node ids. Every member is a node declared in `nodes`, of the
family's declared `type` — a family is a name for a set of existing nodes,
not a place that creates them.

**A family is never itself a node.** It holds no value and carries no
`value_progression`; each member keeps its own, exactly as it would if the
family didn't exist. A reader that collapses a family into a single pool has
violated the never-shared rule the notation exists to preserve — the
differentiated, non-fungible resource design this schema already commits to
above, not a rule invented for families. Seven proficiency pools named by a
family are still seven pools; the family is a way to address them together,
not a seventh, bigger pool that replaces them.

**The `@` sigil.** A reference to a family is written `@<name>`, alongside
`#` for a connection and bare for a node — the third and last member of that
sigil set. `@<name>` may appear anywhere a `from` or `to` accepts a
reference.

**At most one end.** A family reference may appear on at most one end of a
connection. Both ends is invalid: the Cartesian product of two N-member
families would be unauditable, and no real case needs it. A **declaration** —
a `connections:` entry whose `from` or `to` references a family via
`@<name>` — pairs one family against one concrete node (or connection, on a
`state` edge) — never a family against a family.

**Expansion.** A declaration written over a family expands to one connection
per member: a family of seven pools referenced by one declaration produces
seven connections, one per member. **The expanded graph is derived; the file
stores the family and the declarations that reference it, never the
expansion.** This is load-bearing, not a style preference: every write
re-serializes the file's frontmatter from what it declares and nothing
else, so an edge that existed only in the expanded form — and not as the
family plus the declaration over it — would never reach the file. Expansion is
deterministic substitution with no judgement in it, which is what makes
storing only the source and deriving the rest safe.

**`applies: one-of-family`.** A state connection written as a declaration
over a family may carry `applies: one-of-family`, meaning exactly one of the
expanded edges is live at a time. Absent, all expanded edges are live
simultaneously — the plain reading of a family declaration already applies to
a `state` connection as much as to any other. This is what lets a set of
mutually exclusive state edges record what it actually is: seven identical
declarations over a family look like seven simultaneous dependencies, when
only one is ever live. A renderer states the property on the declaration it
qualifies and never presents a `one-of-family` declaration as N simultaneous
edges — doing so restates the exact overstatement the field exists to remove.
A consumer that must act on liveness — a simulator — models neither all N nor
a member of its own choosing, and refuses to model the declaration: what this
field records is *that* exactly one edge is live, and the condition selecting
*which* one is out of scope, which this schema does not model.

**Derived ids.** Each expanded connection's id is
`<declaration-id>:<member-id>`. It is unique by construction and is never
written into the file — a reader computes it from the declaration and the
member, the same substitution that produces the connection itself. This is
what the reservation of `:` in authored connection ids (above) is for: an
authored id may not contain `:`, so a derived id built from two authored ids
joined by `:` cannot collide with one.

**Two-level addressing.** `#<declaration-id>` names the declaration, and so
all of its expanded connections; `#<declaration-id>:<member-id>` names
exactly one of them. Given a declaration `regen` written over a
seven-member family, `#regen` refers to all seven expanded edges and
`#regen:stamina` refers to the one over the `stamina` member alone.

**Stated once, referenced by readers.** This is the only place the expansion
rule is stated. `game-gdd` and `game-critique` reference it rather than
restate it — the same deference they already give the rest of this file's
record shape, needing no new rule to carry it here. **No expansion script
exists**, and expansion is not delegated to one: an expander would
necessarily know families, connections, and the sigils, making it a second
parser of this format regardless of how the bytes reached it.

## Editing the economy graph

Once `design/economy.md` exists, `scripts/economy-tool` is how its
frontmatter changes: it adds, removes, and renames nodes, connections, and
families, sets a node's `value_progression`, answers queries about the graph,
and runs family detection — one command per change, so a one-edge change
never means re-typing the file. It writes the frontmatter only. Every prose
section under the closing `---` stays yours to write and rewrite, per
`game-authoring`; the tool leaves every byte of it as it found it.

Run it from the consuming project's own working directory, with `<skill>`
the directory this file sits in:

```
python3 <skill>/scripts/economy-tool <command> [options]
```

Its commands and options live in its own usage text — `--help`, or
`<command> --help` — and are not restated here, for the same reason
`curve-fit.sh`'s contract is not (below).

Every change is checked before it lands. The tool applies it in memory,
validates the whole graph against this file's rules, and writes only if the
result is valid, setting `updated` to the current UTC minute. A refused
change writes nothing and prints one message naming the record, the rule,
and the fix; relay it to the owner rather than working around it. Two
refusals protect what a command was not asked to touch: `remove-node` and
`remove-connection` refuse while anything still references what they would
remove, and every change refuses a file whose frontmatter is not already in
the one canonical form the tool writes — block-style nodes and families, one
flow-style line per connection — rather than silently reformatting it.

The tool never rewrites prose. After `rename-node` or `remove-node` it
prints each body line still naming the old id; rewrite each, per
`game-authoring`, before the next render — a `## <old-id>` heading left
behind resolves to nothing. `economy-tool validate` checks the whole file,
body headings included, without writing, and notes each `state` connection
still missing its `subtype`. Other records cite nodes, families, and
connections too; `game-gdd`'s `scripts/find_references.py` lists them.

## Fitting a value progression

A node whose value changes over levels or over time is elicited as a raw
series — the owner names a cost at level 1, then at level 2, and so on — and a
list of numbers is not yet a `value_progression`. Turning one into the other
is a step this skill performs with a companion script,
`scripts/curve-fit.sh`, rather than by reasoning about the numbers in prose.
Choosing a curve by eye is exactly the kind of judgement that reads as
confident and lands wrong, and an owner who later asks "why this curve?"
deserves a coefficient of determination rather than a recollection.

The procedure, once per node that has a value series:

1. Collect that node's series from what the owner gave you, as x/y pairs — x
   the level, tier, or time index the value is indexed by, y the value at it.
2. Run the script's `fit` verb over the series. If the owner has already said
   what shape the progression should be, pass that model. If the shape is
   itself the open question, pass `auto` and let the fit choose among the
   families the data admits.
3. Write the fields the script prints into that node's `value_progression`
   object, unchanged, with `economy-tool set-value-progression <node>
   --model … --coefficients … --domain … --fit …`, one flag per printed
   field. They are named to match the four sub-fields declared above, so
   the mapping is one to one and needs no translation — and the reported
   fit travels with the coefficients, so a later reader can see how well
   the curve actually described the series rather than trusting that it
   did.
4. If the script refuses, do not fit the curve by hand and do not quietly
   substitute a shape it rejected. A refusal means the series does not
   support the model asked of it. Report it to the owner, and either collect
   more points or settle which shape they meant.

The script's contract — its verbs, its options, the families it fits, and the
constraint each one refuses on — lives in its own usage text; run it with no
arguments to read it. That contract is deliberately not restated here: two
copies of it would drift, and the copy in this file is the one nobody runs.
For the same reason no curve formula appears anywhere in this file. The
arithmetic lives in exactly one place, and this skill reaches it only by
calling the script.

The script reads and writes no files at all. It takes points as arguments and
prints numbers; finding the node in `design/economy.md` and editing its
frontmatter are `economy-tool`'s work, not this script's. That split is
deliberate — `economy-tool` edits the file through the one parser
`game-gdd` renders it with, so there is still one parser for the economy
file rather than two, and this script's own behaviour stays testable
without a game project to point it at.

The same script carries a second verb, `ev`, for the expected value of a
probability table — a drop table, a randomised reward, a chance-gated `gate`.
Reach for it when a node's value is a distribution rather than a series, and
record what it prints in that node's prose notes: `value_progression` holds a
curve over a domain, not a single expected number, so an expected value does
not belong in that field.

## Accommodated future extensions (not implemented here)

Three balancing techniques came up in the research this skillset is built
from, and each is a documented accommodation — named so a reader learns it
was considered, not silently absent — rather than something this skill
builds:

- **Elo-based skill-rating balance** would consume outcomes recorded per
  player or per strategy against the `converter`/`trader` nodes those
  outcomes pass through, and would write a rating back as a new field on the
  relevant node — the node/connection graph is the hook, and no such field
  exists yet.
- **Monte Carlo simulation balancing** would run the economy graph — its
  nodes, its connections, and any `value_progression` series already fitted
  — forward over simulated time to see where a resource pools up or drains
  out faster than intended. The graph and the value-progression series are
  exactly the data such a pass would consume; nothing here runs a
  simulation.
- **MCTS-based dominant-strategy analysis** would search the space of
  choices a player can make through this same graph — which nodes to feed,
  which `gate`s to pass — for a strategy that dominates the others, again
  consuming the graph and its `value_progression` data as its model of the
  game rather than requiring a second one.

None of the three is implemented by this skill. The schema above already
carries what they need: the required `id`, the sigil rule, and a `state`
connection's `#<connection-id>` target are what let the Monte Carlo
extension above read which flow a state edge multiplies — none of the three
needs a fresh field.
