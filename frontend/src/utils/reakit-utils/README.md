# Contents

This directory contains utilities from
[`reakit-utils` version 0.15.2](https://github.com/ariakit/ariakit/tree/f05d36daa6fbcc52c70cf2c71baea69025aa2402/packages/reakit-utils)
.

We cannot use Reakit/Ariakit directly as it imports React's JSX types
(`@types/react`) which conflict with Vue's own JSX types (`@vue/runtime-dom`).
[Ariakit has essentially the same issue as Storybook, for the moment](https://github.com/storybookjs/storybook/issues/12505).
