// Built-in sample programs shown in the editor's sample dropdown.
// "default" is loaded automatically and is intentionally chosen to
// produce a dramatic, obvious difference between the before/after
// flowcharts (a constant-condition branch collapses entirely).

export const SAMPLES = [
  {
    id: "default",
    name: "Default – branch collapse",
    description: "A constant if-condition folds away and the whole branch disappears from the optimized flowchart.",
    code: `int x = 10;
int y = 20;
int z = x + y;

if (1) {
   z = z + 0;
   print(z);
} else {
   z = 999;
   print(z);
}`,
  },
  {
    id: "constant-folding",
    name: "Sample 1 – Constant folding",
    description: "Arithmetic on literal numbers is evaluated at compile time.",
    code: `int x = 10 + 20;
int y = x * 1;
print(y);`,
  },
  {
    id: "constant-branch",
    name: "Sample 2 – Constant branch",
    description: "An always-true condition removes the diamond and the unreachable else branch.",
    code: `int x = 10;

if (1) {
    x = x + 0;
} else {
    x = 100;
}

print(x);`,
  },
  {
    id: "while-loop",
    name: "Sample 3 – While loop",
    description: "Demonstrates a loop back-edge in the control flow graph.",
    code: `int x = 0;

while (x < 5) {
    x = x + 1;
}

print(x);`,
  },
  {
    id: "multi-optimization",
    name: "Sample 4 – Multiple optimizations",
    description: "Combines constant folding, algebraic simplification and dead-store elimination in one program.",
    code: `int a = 5 * 2;
int b = a + 0;
int c = 100;
c = 7;
int d = c * 0;
print(b);
print(c);
print(d);`,
  },
];

export const DEFAULT_SAMPLE = SAMPLES[0];
