/*
 * Decompiled with CFR 0.152.
 */
package jnode.modelEntities;

import java.io.Serializable;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Set;

public class ClassAnalysis
implements Serializable {
    private String name;
    private Set<String> clusterClasses = new HashSet<String>();
    private Set<String> classesesForDependee = new HashSet<String>(0);
    private Set<String> classesesForDependency = new HashSet<String>(0);
    private double w;
    private double sig;
    private int Noise;
    private int NoiseSuspect;

    public void addToClusterClasses(ClassAnalysis add) {
        this.clusterClasses.add(add.getName());
    }

    public Set<String> getClusterClasses() {
        return this.clusterClasses;
    }

    public void setClusterClasses(Set<String> clusterClasses) {
        this.clusterClasses = new HashSet<String>();
        this.clusterClasses.addAll(clusterClasses);
    }

    public Set<String> getClassesesForDependee() {
        return this.classesesForDependee;
    }

    public void setClassesesForDependee(Set<String> classesesForDependee) {
        this.classesesForDependee = classesesForDependee;
    }

    public Set<String> getClassesesForDependency() {
        return this.classesesForDependency;
    }

    public void addClassForDependency(ClassAnalysis temp) {
        this.classesesForDependency.add(temp.getName());
    }

    public void addClassForDependency(String temp) {
        this.classesesForDependency.add(temp);
    }

    public void addClassForDependendee(ClassAnalysis temp) {
        this.classesesForDependee.add(temp.getName());
    }

    public void addClassForDependendee(String temp) {
        this.classesesForDependee.add(temp);
    }

    public void setClassesesForDependency(Set<String> classesesForDependency) {
        this.classesesForDependency = classesesForDependency;
    }

    public void resetClassesForDependee() {
        this.classesesForDependee = new HashSet<String>(0);
    }

    public String getName() {
        return this.name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public double getSig() {
        return this.sig;
    }

    public void setSig(double sig) {
        this.sig = sig;
    }

    public double getW() {
        return this.w;
    }

    public void setW(double w) {
        this.w = w;
    }

    public int getNoise() {
        return this.Noise;
    }

    public void setNoise(int Noise) {
        this.Noise = Noise;
    }

    public boolean isDependency(String className) {
        // EPL484 performance patch: hash lookup instead of iterating the set
        return this.classesesForDependency.contains(className);
    }

    public int getNoiseSuspect() {
        return this.NoiseSuspect;
    }

    public void setNoiseSuspect(int NoiseSuspect) {
        this.NoiseSuspect = NoiseSuspect;
    }
}

