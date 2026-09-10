# `analytics-configuration`

Ensures a correct Openverse analytics event name and payload configuration.

The rule concerns the configuration of
[the `Events` type](https://github.com/WordPress/openverse/blob/HEAD/frontend/src/types/analytics.ts#L16)
and uses information derived from the behaviour of
[the `useAnalytics` composable](https://github.com/WordPress/openverse/blob/HEAD/frontend/src/composables/use-analytics.ts).
Specifically, the recommended rule configuration depends on the list of default
payload items that `useAnalytics` automatically includes with every custom
event.

Enforces the following conventions:

- Event names must be in screaming snake case
- Events with no payload must define the payload type as `never`
- Event payload property names must not overlap the default payload properties
  supplied by `useAnalytics`
- Event payload values must conform to the value types allowed by Plausible (our
  analytics provider)

```{caution}
Because the rule does not operate with type information, it has no way to verify that
referenced types are value payload values! This means maintainers must be vigilant
when using type references as payload value types to confirm that the type only allows
valid payloads.
```

## Rule Details

Examples of **incorrect** code using this rule:

````{admonition} Incorrect
:class: error

```ts
type Events = {
  /* Incorrect event names */
  eventNameNotInScreamingSnakeCase: never
  event_name_not_in_screaming_case: never
  DANGLING_UNDERSCORE_: never

  /* Incorrect empty payloads */
  INVALID_EMPTY_PAYLOAD: {}
  NULL_PAYLOAD: null
  UNDEFINED_PAYLOAD: undefined

  /* Incorrect payload values */
  OBJECT_PAYLOAD_VALUE: {
    invalidPayloadValueType: {
      foo: string
    }
  }
  NONSENSE_PAYLOAD_VALUE: {
    nonsense: 'one' & 'two' // resolves to `never`, doesn't make any sense
  }

  /* Incorrect payload properties */
  OVERLAPPING_DEFAULT_PAYLOAD_PROP: {
    ua: number
  }
}
```
````

Examples of **correct** code using this rule:

````{admonition} Correct
:class: tip

```ts
type Events = {
  /* Correct event names */
  SINGLEWORDEVENTNAME: never
  MULTI_WORD_EVENT_NAME: never

  /* Correct empty payloads */
  EMPTY_PAYLOAD: never

  /* Correct payload values */
  UNION_PAYLOAD_VALUE: {
    foo: 'one' | 'two' | 'three'
    bar: 1 | 'hello'
  }
  TYPE_REFERENCE_VALUE: {
    foo: SearchType
  }
  SIMPLE_PAYLOAD_VALUES:{
    foo: string
    bar: number
    baz: boolean
  }

  /* Correct payload properties */
  PAYLOAD_PROPS: {
    notADefaultPropName: string
  }
}
```
````
