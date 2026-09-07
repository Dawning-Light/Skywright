---
name: game-mechanics
description: Use when a game project needs its mechanics, systems, and economy written down as structured data rather than prose — eliciting mechanic entries and an economy graph from the owner and writing both into the consuming project's `design/` directory. Not for setting pillars (see `game-pillars`) or rendering a GDD from data that already exists (see `game-gdd`).
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
eliciting mechanics. A suggested order exists across the wider skillset —
`game-pillars` before this skill, this skill before `game-gdd` — but it is
suggested, not enforced: nothing here refuses to run for their absence.

## Process

Elicit conversationally, in whatever order the owner naturally gives it:

1. **Mechanics.** For each mechanic the owner describes, ask enough to fill
   out one mechanic entry (below): what it is, where it sits relative to
   other mechanics already elicited (its parent, if any; its children, if
   any), one strong example of it working as intended, one weak example of
   it failing or being misused.
2. **Systems and economy.** Ask what resources exist, where they enter play,
   where they leave, and what moves or gates them. Map each answer onto a
   node or a connection in the economy graph (below) as it's given, rather
   than collecting free-form notes first and translating them at the end —
   translating late is where a `pool` gets described as a `trader` because
   the distinction blurred in the gap between hearing it and writing it down.

Write each mechanic entry as it is settled, not in a final batch — a mechanic
described early in the conversation and never revisited should already be a
file by the time the conversation ends. Write `design/economy.md` once the
graph stabilizes, and re-write it (not append to it) on any later invocation
that adds or edits nodes or connections.

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

Keeping `parent`/`children` as filenames rather than prose is what makes the
taxonomy walkable: a later skill (or a human) can traverse the whole
mechanics tree by following slugs from file to file, without re-parsing
prose to figure out what points at what.

Body, one heading per field so a reader and a renderer see the same
structure:

- `## Description` — what the mechanic is and how it operates.
- `## Strong example` — one worked case of this mechanic doing what it's for.
- `## Weak example` — one worked case of this mechanic failing, being
  misused, or producing an outcome the design didn't want.

A mechanic entry with no `## Weak example` is incomplete: the point of
naming a failure mode is that it's what a later critique pass (see
`game-critique`) checks a design against.

## The economy graph

One file for the whole graph, at `design/economy.md` in the consuming
project — a Machinations-style node/connection representation of how
resources move through the game.

Frontmatter carries `nodes` and `connections`.

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

**Meeting a file whose connections have no `id`.** A file written before this
restructuring has connections with no `id`, no sigils on `from`/`to`, and no
`subtype`. Meeting one, this skill neither silently re-writes it into the new
shape nor refuses to proceed with the write already under way. It reports
which behaviours the file fails and puts the upgrade to the owner; a
confirmed upgrade is performed as part of that same write, and a declined one
leaves the file exactly as it is.

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
families would be unauditable, and no real case needs it. A declaration
pairs one family against one concrete node (or connection, on a `state`
edge) — never a family against a family.

**Expansion.** A declaration written over a family expands to one connection
per member: a family of seven pools referenced by one declaration produces
seven connections, one per member. **The expanded graph is derived; the file
stores the family and the declarations that reference it, never the
expansion.** This is load-bearing, not a style preference: this skill
rewrites the economy file wholesale on every invocation, so anything that
existed only as the expanded form — and not as the family plus the
declaration over it — would not survive the next write. Expansion is
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
what step 2's reservation of `:` in authored connection ids was for: an
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
   object, unchanged. They are named to match the four sub-fields declared
   above, so the mapping is one to one and needs no translation — and the
   reported fit travels with the coefficients, so a later reader can see how
   well the curve actually described the series rather than trusting that it
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
prints numbers; opening `design/economy.md`, finding the node, and editing
its frontmatter are this procedure's work, not the script's. That split is
deliberate — it keeps one parser for the economy file rather than two, and it
keeps the script's own behaviour testable without a game project to point it
at.

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
rests on a restructuring rather than an addition: the required `id`, the
sigil rule, and a `state` connection's new `#<connection-id>` target are what
let the Monte Carlo extension above read which flow a state edge multiplies —
none of the three needed a fresh field bolted on afterward.
