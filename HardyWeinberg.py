#!/usr/bin/env python

"""Module for calculating Hardy-Weinberg statistics.

"""

import string, sys, os

class HardyWeinberg:
  """Calculate Hardy-Weinberg statistics.

  Given the observed genotypes for a locus, calculate the expected
  genotype counts based on Hardy Weinberg proportions for individual
  genotype values, and test for fit.

  """

  def __init__(self, locusData, alleleCount, debug=0):
    """Constructor.

    - locusData and alleleCount to be provided by driver script
      via a call to ParseFile.getLocusData(locus).

    """

    self.locusData = locusData

#     we can't use the alleleCount data at the moment
#     because ParseFile.getAlleleCountAt() returns unclean data
#     self.alleleCounts = alleleCount[0] #just the dictionary of allelename:count
#     self.alleleTotal = alleleCount[1]

    self.debug = debug

    self.n = len(self.locusData)
    self.k = 2 * self.n

    self._generateTables()
    self._calcChisq()

#     if self.debug:
#       self.counter = 0
#       for genotype in self.locusData:
#         self.counter += 1
#         print genotype
#       print "Population:", self.n
#       print "Alleles:", self.k
#       print 'Given:', self.alleleTotal
#       print'Counter:', self.counter
#       print self.alleleCount
#       running_count = 0
#       running_freq = 0.0
#       for allele in self.alleleCount.keys():
#         running_count += self.alleleCount[allele]
#         #freq = self.alleleCount[allele] / float(self.k)
#         freq = self.alleleCount[allele] / float(self.alleleTotal)
#         running_freq += freq
#         print allele, 'obs:', self.alleleCount[allele],\
#                       'count:', running_count,\
#                       'freq:', freq,\
#                       'cum:', running_freq
################################################################################
  def _generateTables(self):
    """Manipulate the given genotype data to generate
    the tables upon which the calculations will be based."""

    self.alleleCounts = {}
    self.alleleFrequencies = {}
    self.observedGenotypes = []
    self.observedAlleles = []               # need a uniqed list
    self.observedGenotypeCounts = {}
    self.possibleGenotypes = []
    self.expectedGenotypeCounts = {}
    
    self.alleleTotal = 0

    for genotype in self.locusData:
      """Run through each tuple in the given genotype data and
      create a dictionary of allele counts"""

      self.alleleTotal += 2
      if self.alleleCounts.has_key(genotype[0]):
        self.alleleCounts[genotype[0]] += 1
      else:
        self.alleleCounts[genotype[0]] = 1
      if self.alleleCounts.has_key(genotype[1]):
        self.alleleCounts[genotype[1]] += 1
      else:
        self.alleleCounts[genotype[1]] = 1

      if genotype[0] not in self.observedAlleles:
        self.observedAlleles.append(genotype[0])
      if genotype[1] not in self.observedAlleles:
        self.observedAlleles.append(genotype[1])

      self.observedGenotypes.append(genotype[0] + ":" + genotype[1])

    frequencyAccumulator = 0.
    for allele in self.alleleCounts.keys():
      """For each entry in the dictionary of allele counts
      generate a corresponding entry in a dictionary of frequencies"""

      freq = self.alleleCounts[allele] / float(self.k)
      frequencyAccumulator += freq
      self.alleleFrequencies[allele] = freq

    for genotype in self.observedGenotypes:
      """Generate a dictionary of genotype:count key:values"""

      # maybe this should be a copy of possibleGenotypes with zeroes where
      # there are no observations???
      if self.observedGenotypeCounts.has_key(genotype):
        self.observedGenotypeCounts[genotype] += 1
      else:
        self.observedGenotypeCounts[genotype] = 1

    for i in range(len(self.observedAlleles)):
      """Generate a list of all possible genotypes"""

      for j in range(i, len(self.observedAlleles)):
          self.possibleGenotypes.append(self.observedAlleles[i] + ":" + self.observedAlleles[j])

    for genotype in self.possibleGenotypes:
      """Calculate expected genotype counts under HWP

      - Create a dictionary of genotype:frequency key:values"""

      temp = string.split(genotype, ':')
      if temp[0] == temp[1]:         # homozygote, N * pi * pi
        self.expectedGenotypeCounts[genotype] = self.n * self.alleleFrequencies[temp[0]] * self.alleleFrequencies[temp[1]]
      else:                          # heterozygote, 2N * pi * pj
        self.expectedGenotypeCounts[genotype] = 2 * self.n * self.alleleFrequencies[temp[0]] * self.alleleFrequencies[temp[1]]

    total = 0
    for value in self.expectedGenotypeCounts.values():
      """Check that the sum of expected genotype counts approximates N"""

      total += value
    if abs(float(self.n) - total) > float(self.n) / 1000.0:
      print 'AAIIEE!'
      print 'Calculated sum of expected genotype counts is:', total, ', but N is:', self.n
      sys.exit()

    if self.debug:
#       print 'Allele Frequencies:'
#       for allele in self.alleleFrequencies.items():
#         print allele
#       print 'Cumulative frequency:', frequencyAccumulator
#       print 'Total allele count:', self.alleleTotal
#       print '\nGenotype counts:'
#       print 'Possible:'
#       for genotype in self.possibleGenotypes:
#         print genotype
      print 'Observed:'
      for genotype in self.observedGenotypeCounts.items():
        print genotype
      print 'Expected:'
      for genotype in self.expectedGenotypeCounts.items():
        print genotype

################################################################################

  def _calcChisq(self):
    """Calculate the chi-squareds for the common genotypes.

    - create a count of observed and expected lumped together
    for genotypes with an expected value of less than 5

    - Open a pipe to get the p-value from the system
    using the pval program (should be replaced later)"""

    self.printExpected = [] # list flagging genotypes worth printing
    self.chisq = {}
    self.chisqPval = {}
    self.commonGenotypeCounter = 0
    self.commonChisqAccumulator = 0.0
    self.rareGenotypeCounter = 0
    self.lumpedObservedGenotypes = 0.0
    self.lumpedExpectedGenotypes = 0.0
    # print 'Calculating Chi Squared'

    #--mpn--
    for genotype in self.expectedGenotypeCounts.keys():
      if self.expectedGenotypeCounts[genotype] > 4.99:
        if self.debug:
          print 'Expected:'
          print genotype, self.expectedGenotypeCounts[genotype]
          if self.observedGenotypeCounts.has_key(genotype):
            print 'Observed:', self.observedGenotypeCounts[genotype]
          else:
            print 'Observed: 0'

        self.printExpected.append(genotype)

        self.commonGenotypeCounter += 1
        if self.observedGenotypeCounts.has_key(genotype):
          observedCount = self.observedGenotypeCounts[genotype]
        else:
          observedCount = 0.0
        self.commonDfAccumulator = self.commonGenotypeCounter - 1
        self.chisq[genotype] = ((observedCount - \
                          self.expectedGenotypeCounts[genotype]) * \
                          (observedCount - \
                          self.expectedGenotypeCounts[genotype])) /\
                          self.expectedGenotypeCounts[genotype]

        command = "pval 1 %f" % (self.chisq[genotype])
        returnedValue = os.popen(command, 'r').readlines()
        self.chisqPval[genotype] = returnedValue[0][:-1]
        self.commonChisqAccumulator += self.chisq[genotype]

        if self.debug:
          print 'Chi Squared value:'
          print genotype, ':', self.chisq[genotype]
          # print "command %s returned %s" % (command, returnedValue)
          print 'P-value:'
          print genotype, ':', self.chisqPval[genotype]

      else:
        """Expected genotype count for this genotype is less than 5"""

        # do not append this genotype to the printExpected list
        self.rareGenotypeCounter += 1

        self.lumpedExpectedGenotypes += self.expectedGenotypeCounts[genotype]

        if self.observedGenotypeCounts.has_key(genotype):
          self.lumpedObservedGenotypes += self.observedGenotypeCounts[genotype]


    if self.rareGenotypeCounter > 0:
      """ Calculate the Chi Squared value for the lumped rare genotypes"""

      self.lumpedChisq = ((self.lumpedObservedGenotypes - self.lumpedExpectedGenotypes) * \
                         (self.lumpedObservedGenotypes - self.lumpedExpectedGenotypes) / \
                         self.lumpedExpectedGenotypes)

      command = "pval 1 %f" % (self.lumpedChisq)
      returnedValue = os.popen(command, 'r').readlines()
      self.lumpedChisqPval = returnedValue[0][:-1]

      if self.commonGenotypeCounter > 0:
        self.HWChisq = self.commonChisqAccumulator + self.lumpedChisq
        self.HWChisqDf = self.commonDfAccumulator + 1
        command = "pval %f %f" % (self.HWChisqDf, self.HWChisq)
        returnedValue = os.popen(command, 'r').readlines()
        self.HWChisqPval = returnedValue[0][:-1]

      if self.debug:
        print "Lumped %d for a total of %d observed and %f expected" % (self.rareGenotypeCounter, self.lumpedObservedGenotypes, self.lumpedExpectedGenotypes)
        print "Chisq: %f, P-Value (dof = 1): %s" % (self.lumpedChisq, self.lumpedChisqPval) # doesn't work if I claim Pval is a float?

    elif self.commonGenotypeCounter > 0:
      self.HWChisq = self.commonChisqAccumulator
      self.HWChisqDf = self.commonDfAccumulator

      command = "pval %d %f" % (self.commonDfAccumulator, self.commonChisqAccumulator)
      returnValue = os.popen(command, 'r').readlines()

      self.HWChisqPval = returnValue[0][:-1]

################################################################################

  def getChisq(self):
    """ Output routines depend on existence or otherwise of common and rare genotypes"""

    # stream serialization goes here
    if self.commonGenotypeCounter == 0:
      print "No common genotypes; chi-square cannot be calculated"

    elif self.rareGenotypeCounter == 0:

      print "HWChisq    :", self.HWChisq
      print "HWChisqDf  :", self.HWChisqDf
      print "HWChisqPval:", self.HWChisqPval
      print "No lumps"

    else:
      print "Sample size:", self.n
      print "Alleles:   :", self.k
      print "Chi Squared:", self.HWChisq
      print "DoF        :", self.HWChisqDf
      print "HWChisqPval:", self.HWChisqPval
      print ""
      print "Lumped observed:", self.lumpedObservedGenotypes
      print "Lumped expected:", self.lumpedExpectedGenotypes
      print "Lumped Chisq   :", self.lumpedChisq
      print "Lumped Pval    :", self.lumpedChisqPval


