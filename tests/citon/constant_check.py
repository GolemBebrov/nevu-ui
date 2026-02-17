from nevu_ui.fast.nvparam import NvParam

const = NvParam("const", 1, 1, 1, int)

print(f"repr: {const}")
print("correct check:", const.check(1))
print("wrong check:", const.check("1"))

const.value = 2

print("changed value manually:", const.value)

const.reset()

print("reseted value:", const.value)

nomanu = lambda x: x+1
const.setter = nomanu
const.set(3)
print("changed value via setter:", const.value)

