import cplex
import sys
import matplotlib.pyplot as plt
import numpy

TOLERANCE =10e-6 
################## Data Class #################

class DietData:
    def __init__(self):
        self.n = 0
        self.m = 0
        self.cost = []
        # Info related to nutrients.
        self.nutr = {}
        self.reqs = {}
        self.perc = 0
        self.req_names = []

    def get_contrib(self, x, key):
        ret = 0
        for i in range(len(x)):
            ret += x[i]*self.nutr[key][i]
        return ret

    def load(self, filename):
        f = open(filename)

        # Read general data
        line = f.readline().split(' ')
        self.n = int(line[0])
        self.m = int(line[1])

        # Read costs
        line = f.readline().split(' ')
        self.cost = [float(i) for i in line]

        # Read remaining nutrients
        for i in range(self.m):
            line = f.readline().split(' ')
            self.req_names.append(line[0])
            self.reqs[line[0]] = float(line[1])
            self.nutr[line[0]] = [float(k) for k in line[2:]]
    
    def _data_check(self):
        pass

    def __repr__(self):
        ret = ''
        ret += 'n = %d\nm = %d\nperc = %d\n' % (self.n,self.m,self.perc)
        ret += 'cost: %s\n' % (','.join([str(x) for x in self.cost]))
        ret += 'nutr:\n'
        for k in self.nutr:
            ret += '\t%s: %s\n' % (k,','.join([str(x) for x in self.nutr[k]]))
        ret += 'reqs. nutr.:\n'
        for k in self.reqs:
            ret += '\t%s: %d\n' % (k,self.reqs[k])

        return ret

################## Helper Functions ##################

def get_instance_data(filename):
    """
    Loads filename and generate instance of DietData class

    :param filename: name of txt file with instance
    :return: instance of DietData
    """

    data = DietData()
    data.load(filename)

    return data

def add_constraint_matrix(myprob, data):
    """
    Adds constraint matrix to CPLEX optimization model.

    :param myprob: instance of CPLEX optimization problem (LP)
    :param data: matrix with constraints (one per row)
    :return:
    """

    # data.nutr[j] contains contribution of each food for nutrient j
    # data.reqs[j] contains b_j value for nutrient j
    
    # Index generation
    ind = list(range(data.n))
    requirements = data.req_names
    #k_value = list(range(data.perc))

    # Add "greater or equal" (1-k) constraints
    for i in requirements:
        val = data.nutr[i]
        row = [ind, val]
        myprob.linear_constraints.add(lin_expr=[row], senses=['G'], rhs=[(1-data.perc)*data.reqs[i]])

    # Add "lower or equal" (1+k) constraints
    for i in requirements:
        val = data.nutr[i]
        row = [ind, val]
        myprob.linear_constraints.add(lin_expr=[row], senses=['L'], rhs=[(1+data.perc)*data.reqs[i]])
        
   

def populate_by_row(myprob, data):
    """
    Builds CPLEX Model by adding variables, setting the optimization function objective and constraint matrix.
    Writes model to file.
    :param myprob: instance of CPLEX optimization problem (LP)
    :param data: matrix with constraints
    :return: lp file with linnear model
    """

    # Add variables (and lower bounds)
    myprob.variables.add(obj = data.cost, lb = [0]*data.n)

    # Set problem objective as minimization
    myprob.objective.set_sense(myprob.objective.sense.minimize)
    
    # Add constraint matrix
    add_constraint_matrix(myprob, data)
    
    # Export myprob LP (useful for debugging)
    myprob.write('test_diet.lp')
    

def solve_lp(myprob):
    """
    Solves the linnear program

    :param myprob: properly defined instance of CPLEX optimization problem (with objective, variables and constraints)
    :return: problem's solution
    """

    # Solve LP
    myprob.solve()

    # Get solution's information
    # Variables values
    x = myprob.solution.get_values()
    # Objective function value
    f_obj = myprob.solution.get_objective_value()
    # Solution's status
    stat = myprob.solution.get_status()
    stat_str = myprob.solution.get_status_string(status_code = stat)

    print('Objective function: ',f_obj)
    print('Status solution: ', stat_str,'(' + str(stat) + ')')

    # Print variables > TOLERANCE (active variables)
    for i in range(len(x)):
        if x[i] > TOLERANCE:
            print("x_" + str(i) + " = " , x[i] )    



def plot_two_series(x, y, z, target, name_y = '', name_z = ''):
    """
    Plots series for lists (x,y) and (x,z).

    :param x: list
    :param y: list
    :param z: list
    :param target:
    :param name_y:
    :param name_z:
    :return:
    """

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax2 = ax.twinx()
    
    LB = target * (1 - x) # Lower bound
    UB = target * (1 + x) # Upper bound
    
    lns1 = ax2.plot(x, y, 'x-', label = name_y, color = 'g', alpha = 0.8)
    lns2 = ax.plot(x, z, 'o-', label = name_z, alpha = 0.8)
    lnsLB = ax.plot(x, LB, linestyle = '--', label = 'Tolerance ' + name_z, color = 'r', alpha = 0.4)
    lnsUB = ax.plot(x, UB, linestyle = '--', color = 'r', alpha = 0.4)
    

    # added these three lines
    lns = lns1+lns2+lnsLB
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc=3)
    ax.set_title('Variation ' + name_z + ' y Cost by k')
    ax.set_xlabel('k')
    ax.set_ylabel(name_z)
    ax.set_ylim(min(LB)*0.9, max(UB)*1.1)
    ax2.set_ylabel('Cost')

    fig.tight_layout()
    plt.show()



################## Main ##################

def main(filename):
    import os
    os.chdir('C:/Repo/Github/combinatorial_optimization/diet_problem/')

    # Instantiate DietData
    data = DietData()

    # Load data
    data.load("diet1.in")

    #print("printing values")
    #print(data.nutr)
    #print(data.req_names)
    
    # Solve model for each value of k
    values_k = numpy.arange(0.01, 0.21, 0.01)
    
    listObj = []
    listCalories = []
    listProteins = []
    listCalcium = []
    
    for i in values_k:
        print()
        print(".............................................")
        print("Calculating for value of k equal to: " + str(i))
        print(".............................................")
        # Assign value to data.perc
        data.perc = i
        # Instantiate CPLEX problema.
        prob_lp = cplex.Cplex()
        # Generate CPLEX model.
        populate_by_row(prob_lp, data)
        # Solve model.
        solve_lp(prob_lp)
        # Store results for plotting
        x = prob_lp.solution.get_values()
        listObj.append(prob_lp.solution.get_objective_value())
        listCalories.append(data.get_contrib(x, data.req_names[0]))
        listProteins.append(data.get_contrib(x, data.req_names[1]))
        listCalcium.append(data.get_contrib(x, data.req_names[2]))
        
    # Contribution Calories by value k
    plot_two_series(values_k, listObj, listCalories, 2000, 'Cost', 'Calories')
    # Contribution Proteins by value k
    plot_two_series(values_k, listObj, listProteins, 55, 'Cost', 'Proteins')
    # Contribution Calcium by value k
    plot_two_series(values_k, listObj, listCalcium, 800, 'Cost', 'Calcium')
    

if __name__ == "__main__":
    #main(sys.argv[1])
    main("diet1.in")