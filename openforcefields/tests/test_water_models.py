import openmm
import pytest
from openff.toolkit import ForceField, Molecule, Topology
from openff.toolkit.tests.utils import compare_system_parameters
from openmm.app import ForceField as OpenMMForceField
from openmm.app import HAngles
from openmm.app import Topology as OpenMMTopology


@pytest.fixture
def water_molecule() -> Topology:
    molecule = Molecule.from_smiles("[H:2][O:1][H:3]")
    molecule.generate_conformers(n_conformers=1)
    return molecule.to_topology()


def compare_water_systems(reference: openmm.System, system: openmm.System):
    # OpenMM creates bond and angle forces despite each containing 0 parameters
    forces_to_remove = list()

    for index, force in enumerate(reference.getForces()):
        if isinstance(force, openmm.HarmonicBondForce):
            assert force.getNumBonds() == 0
            bond_force: int = index

    reference.removeForce(bond_force)

    for index, force in enumerate(reference.getForces()):
        if isinstance(force, openmm.HarmonicAngleForce):
            assert force.getNumAngles() == 0
            angle_force: int = index

    reference.removeForce(angle_force)

    compare_system_parameters(reference, system)


def test_tip3p(water_molecule):
    assert water_molecule.n_atoms == 3

    reference = OpenMMForceField("tip3p.xml").createSystem(
        water_molecule.to_openmm(),
        constraints=HAngles,
        rigidWater=True,
    )

    system = ForceField("water/tip3p-1.0.0.offxml").create_openmm_system(
        water_molecule,
    )

    compare_water_systems(reference, system)


def test_tip3p_fb(water_molecule):
    assert water_molecule.n_atoms == 3

    reference = OpenMMForceField("tip3pfb.xml").createSystem(
        water_molecule.to_openmm(),
        constraints=HAngles,
        rigidWater=True,
    )

    system = ForceField("water/tip3p-fb-1.0.0.offxml").create_openmm_system(
        water_molecule,
    )

    compare_water_systems(reference, system)
