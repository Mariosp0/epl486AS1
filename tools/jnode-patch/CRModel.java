/*
 * Decompiled with CFR 0.152.
 */
package jnode.workers;

import java.util.ArrayList;
import java.util.List;
import jnode.modelEntities.ClassAnalysis;

public class CRModel {
    private List<ClassAnalysis> classes = new ArrayList<ClassAnalysis>();
    private double p = 0.85;
    private double[][] distributionRatios;
    private double[] nodeWeightsBefore;
    private double[] nodeWeightsAfter;

    public CRModel(List<ClassAnalysis> classes1) {
        this.classes.addAll(classes1);
        this.distributionRatios = new double[this.classes.size()][this.classes.size()];
        this.nodeWeightsBefore = new double[this.classes.size()];
        this.nodeWeightsAfter = new double[this.classes.size()];
    }

    public List<ClassAnalysis> getClassAnalysis() {
        return this.classes;
    }

    public void doIt() {
        this.initializeNodeWeights();
        this.startIterationsToConcludeToWeights();
    }

    private void initializeNodeWeights() {
        double temp = this.roundDecimals(1.0 / (double)this.classes.size());
        int i = 0;
        while (i < this.classes.size()) {
            this.nodeWeightsBefore[i] = temp;
            this.nodeWeightsAfter[i] = temp;
            ++i;
        }
    }

    private void startIterationsToConcludeToWeights() {
        int i;
        int iterations = 0;
        do {
            int j;
            if (++iterations > 1) {
                i = 0;
                while (i < this.classes.size()) {
                    double sum = 0.0;
                    j = 0;
                    while (j < this.classes.size()) {
                        sum += this.distributionRatios[j][i];
                        ++j;
                    }
                    this.nodeWeightsBefore[i] = this.roundDecimals(sum);
                    ++i;
                }
            } else {
                int j2 = 0;
                while (j2 < this.classes.size()) {
                    if (this.classes.get(j2).getClassesesForDependency().isEmpty()) {
                        i = 0;
                        while (i < this.classes.size()) {
                            this.distributionRatios[i][j2] = 1.0 / (double)this.classes.size();
                            ++i;
                        }
                    } else {
                        i = 0;
                        while (i < this.classes.size()) {
                            if (!this.classes.get(j2).getClassesesForDependency().contains(this.classes.get(i).getName())) {
                                double val;
                                this.distributionRatios[i][j2] = val = (1.0 - this.p) / (double)this.classes.size();
                            }
                            ++i;
                        }
                    }
                    ++j2;
                }
            }
            i = 0;
            while (i < this.classes.size()) {
                int j3 = 0;
                while (j3 < this.classes.size()) {
                    double value;
                    this.distributionRatios[i][j3] = this.classes.get(i).isDependency(this.classes.get(j3).getName()) ? (value = this.roundDecimals(this.p * (this.nodeWeightsBefore[i] / (double)this.classes.get(i).getClassesesForDependency().size())) + (1.0 - this.p) / (double)this.classes.size()) : this.roundDecimals(1.0 / (double)this.classes.size());
                    ++j3;
                }
                ++i;
            }
            i = 0;
            while (i < this.classes.size()) {
                double sum = 0.0;
                j = 0;
                while (j < this.classes.size()) {
                    sum += this.distributionRatios[j][i];
                    ++j;
                }
                this.nodeWeightsAfter[i] = this.roundDecimals(sum);
                ++i;
            }
        } while (!this.allSameElements(this.nodeWeightsBefore, this.nodeWeightsAfter));
        i = 0;
        while (i < this.classes.size()) {
            this.classes.get(i).setW(this.nodeWeightsAfter[i]);
            ++i;
        }
    }

    private boolean allSameElements(double[] array1, double[] array2) {
        int i = 0;
        while (i < array1.length) {
            if (array1[i] != array2[i]) {
                return false;
            }
            ++i;
        }
        return true;
    }

    private Double roundDecimals(double d) {
        d = (double)Math.round(d * 10000.0) / 10000.0;
        return d;
    }
}

