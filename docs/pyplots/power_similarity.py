import nengo_spa as spa
import matplotlib.pyplot as plt

alg = spa.algebras.HrrAlgebra()
v = alg.create_vector(64, {"positive", "unitary"})

xs = np.linspace(1.0, 2.0)
powers = [alg.binding_power(v, x) for x in xs]
v_sims = [np.dot(v, p) for p in powers]
vv = alg.bind(v, v)
vv_sims = [np.dot(vv, p) for p in powers]

fig = plt.figure()
ax = fig.subplots()

ax.plot(xs, v_sims, label=r"$\vec{v}$")
ax.plot(xs, vv_sims, label=r"$\vec{v}^2$")
ax.set_xlabel("Power $p$")
ax.set_xlim(1.0, 2.0)
ax.set_ylabel(r"Cosine similarity with $\vec{v}^p$")
ax.set_ylim(0.0, 1.0)
ax.legend()

fig.show()