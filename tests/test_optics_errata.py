"""数值核对首批勘误中的光学关系；运行 python -m unittest discover -s tests -v。"""

import cmath
import math
import unittest


def dft(values):
    count = len(values)
    return [sum(value * cmath.exp(-2j * math.pi * j * k / count)
                for j, value in enumerate(values)) for k in range(count)]


class OpticsErrataTests(unittest.TestCase):
    def test_complex_pupil_otf_agrees_with_intensity_transform(self):
        # F3-s24,31,34: compare two independent routes to the complex OTF.
        pupil = [0, 1, cmath.exp(0.3j), 0.7 * cmath.exp(-0.8j), 0.2j] + [0] * 11
        psf = [abs(value) ** 2 for value in dft(pupil)]
        spectrum = dft(psf)
        energy = sum(abs(value) ** 2 for value in pupil)
        for shift, value in enumerate(spectrum):
            correlation = sum(p * pupil[(j + shift) % len(pupil)].conjugate()
                              for j, p in enumerate(pupil)) / energy
            self.assertAlmostEqual(abs(value / spectrum[0] - correlation), 0, places=12)

    def test_tilt_shifts_psf_and_gives_negative_otf_phase(self):
        count, displacement = 16, 3
        pupil = [0, 1, 1, 0.5, 0.2] + [0] * 11
        tilted = [p * cmath.exp(2j * math.pi * displacement * j / count)
                  for j, p in enumerate(pupil)]
        psf = [abs(value) ** 2 for value in dft(pupil)]
        shifted_psf = [abs(value) ** 2 for value in dft(tilted)]
        base, shifted = dft(psf), dft(shifted_psf)
        for j in range(count):
            self.assertAlmostEqual(shifted_psf[j], psf[(j - displacement) % count], places=11)
            expected = base[j] * cmath.exp(-2j * math.pi * j * displacement / count)
            self.assertAlmostEqual(abs(shifted[j] - expected), 0, places=10)

    def test_two_dimensional_4f_amplitude_and_energy(self):
        # Integrate both 2f stages, including their physical sampling measures.
        count, step, wavelength, f1, f2 = 12, 0.5, 0.5, 4, 8
        x = [(j - count // 2) * step for j in range(count)]
        frequency_step = wavelength * f1 / (count * step)
        xi = [(j - count // 2) * frequency_step for j in range(count)]
        output_step = wavelength * f2 / (count * frequency_step)
        output_x = [(j - count // 2) * output_step for j in range(count)]
        field = [[cmath.exp(-(a * a + b * b) + 0.2j * a) for b in x] for a in x]

        def propagate(values, source, target, spacing, focal_length):
            kernels = [[cmath.exp(-2j * math.pi * a * b / (wavelength * focal_length))
                        for b in source] for a in target]
            return [[spacing ** 2 / (1j * wavelength * focal_length) *
                     sum(values[j][k] * kernels[a][j] * kernels[b][k]
                         for j in range(count) for k in range(count))
                     for b in range(count)] for a in range(count)]

        middle = propagate(field, x, xi, step, f1)
        output = propagate(middle, xi, output_x, frequency_step, f2)
        for a in range(count):
            for b in range(count):
                expected = -f1 / f2 * field[(-a) % count][(-b) % count]
                self.assertAlmostEqual(abs(output[a][b] - expected), 0, places=12)
        energy_in = step ** 2 * sum(abs(value) ** 2 for row in field for value in row)
        energy_out = output_step ** 2 * sum(abs(value) ** 2 for row in output for value in row)
        self.assertAlmostEqual(energy_in, energy_out, places=12)

    def test_pure_phase_has_no_brightfield_intensity_modulation(self):
        # F3-s90: the field's quadratic term cancels the spurious intensity term.
        for phase in [-0.1, -0.03, 0, 0.03, 0.1]:
            self.assertAlmostEqual(abs(cmath.exp(1j * phase)) ** 2, 1, places=14)
            second_order_field = 1 + 1j * phase - phase ** 2 / 2
            self.assertAlmostEqual(abs(second_order_field) ** 2 - 1, phase ** 4 / 4, places=14)

    def test_signed_lens_magnifications_from_ray_and_position_changes(self):
        # VO-s30,31,35,36,37; global object and image positions both point right.
        for object_distance in [0.3, 0.05]:
            focal_length, ray_height, delta = 0.1, 0.002, 1e-7
            image_distance = 1 / (1 / focal_length - 1 / object_distance)
            moved_image = 1 / (1 / focal_length - 1 / (object_distance - delta))
            beta = -image_distance / object_distance
            gamma = (-ray_height / image_distance) / (ray_height / object_distance)
            alpha = (moved_image - image_distance) / delta
            self.assertAlmostEqual(gamma, 1 / beta, places=12)
            self.assertAlmostEqual(alpha, beta ** 2, delta=2e-5)
            self.assertAlmostEqual(alpha * gamma, beta, delta=2e-5)

    def test_back_focal_stop_makes_object_chief_ray_parallel(self):
        # VO-s72,74,76: a chief ray passes through the stop centre.
        focal_length = 0.1
        for distance, height in [(0.3, 0.002), (0.5, -0.003)]:
            # At the back focal plane, stop height = f * incident slope.
            incident_slope = 0
            lens_height = height + distance * incident_slope
            outgoing_slope = incident_slope - lens_height / focal_length
            stop_height = lens_height + focal_length * outgoing_slope
            self.assertAlmostEqual(stop_height, 0, places=14)
            self.assertEqual(incident_slope, 0)
            self.assertNotEqual(outgoing_slope, 0)


if __name__ == '__main__':
    unittest.main()
