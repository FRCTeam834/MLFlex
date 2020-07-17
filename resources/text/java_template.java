/*----------------------------------------------------------------------------*/
/* Copyright (c) 2019 FIRST. All Rights Reserved.                             */
/* Open Source Software - may be modified and shared by FRC teams. The code   */
/* must be accompanied by the FIRST BSD license file in the root directory of */
/* the project.                                                               */
/*----------------------------------------------------------------------------*/

package frc.robot.subsystems;

import java.util.ArrayList;

import edu.wpi.first.networktables.NetworkTable;
import edu.wpi.first.networktables.NetworkTableInstance;
import edu.wpi.first.wpilibj2.command.SubsystemBase;

/**
 * Data structure for returned arrays is as follows: 
 * - Each column (first value) represents a space to store object values. 
 * The data structure of the rows is
 * as follows: - 0 or -1, with -1 being not used and 0 being used (meaning data
 * is valid and should be considered) 
 * - objectID - a unique ID for each different object that appears
 * - centerX - the x coordinate of the center
 * - centerY - the y coordinate of the center 
 * - endX - the x coordinate of the bottom right corner of the bounding box 
 * - endY - the y coordinate of the bottom right corner of the bounding box 
 * - area - the area of the bounding box
 * - confidence - the confidence level of the neural network that the object is indeed what it is tagged as
 * Camera resolution is 640 x 480 @ 7 fps.
 */

public class EVSNetworkTables extends SubsystemBase {
  // Put methods for controlling this subsystem
  // here. Call these from Commands.

  @Override
  public void periodic() {
    // Set the default command for a subsystem here.
    // setDefaultCommand(new MySpecialCommand());

  }

  public NetworkTable getVisionTable() {

    // Get the NetworkTables instance and return it
    n = NetworkTableInstance.getDefault();
    NetworkTable evs = n.getTable("EVS");
    return evs;

  }

  public ArrayList<ArrayList<Double>> getPowerCellArray() {

    // Create a new expandable array for the tables
    ArrayList<ArrayList<Double>> visionArray = new ArrayList<ArrayList<Double>>(10);

    // Add each of the object tables to the master array
    visionArray.add(new ArrayList<Double>(0));
    visionArray.add(new ArrayList<Double>(0));
    visionArray.add(new ArrayList<Double>(0));
    visionArray.add(new ArrayList<Double>(0));
    visionArray.add(new ArrayList<Double>(0));
    visionArray.add(new ArrayList<Double>(0));
    visionArray.add(new ArrayList<Double>(0));
    visionArray.add(new ArrayList<Double>(0));
    visionArray.add(new ArrayList<Double>(0));
    visionArray.add(new ArrayList<Double>(0));


    // Start if statement
    if (getVisionTable().getSubTable("Power_Cell0").getEntry("inUse").getBoolean(true)) {

      double powerCellArray[] = getVisionTable().getSubTable("Power_Cell0").getEntry("values").getDoubleArray(new double[7]);

      ArrayList<Double> values = new ArrayList<Double>();

      for (int i = 0; i < 7; i++) {

        values.add(powerCellArray[i]);

      }

      visionArray.set(0, values);

      if (getVisionTable().getSubTable("Power_Cell1").getEntry("inUse").getBoolean(true)) {

        powerCellArray = getVisionTable().getSubTable("Power_Cell1").getEntry("values").getDoubleArray(new double[7]);

        values = new ArrayList<Double>();
        for (int i = 0; i < 7; i++) {

          values.add(powerCellArray[i]);

        }

        visionArray.set(1, values);

        if (getVisionTable().getSubTable("Power_Cell2").getEntry("inUse").getBoolean(true)) {

          powerCellArray = getVisionTable().getSubTable("Power_Cell2").getEntry("values").getDoubleArray(new double[7]);

          values = new ArrayList<Double>();
          for (int i = 0; i < 7; i++) {

            values.add(powerCellArray[i]);

          }

          visionArray.set(2, values);

          if (getVisionTable().getSubTable("Power_Cell3").getEntry("inUse").getBoolean(true)) {

            powerCellArray = getVisionTable().getSubTable("Power_Cell3").getEntry("values")
                .getDoubleArray(new double[7]);

            values = new ArrayList<Double>();
            for (int i = 0; i < 7; i++) {

              values.add(powerCellArray[i]);

            }

            visionArray.set(3, values);

            if (getVisionTable().getSubTable("Power_Cell4").getEntry("inUse").getBoolean(true)) {

              powerCellArray = getVisionTable().getSubTable("Power_Cell4").getEntry("values")
                  .getDoubleArray(new double[7]);

              values = new ArrayList<Double>();
              for (int i = 0; i < 7; i++) {

                values.add(powerCellArray[i]);

              }

              visionArray.set(4, values);

              if (getVisionTable().getSubTable("Power_Cell5").getEntry("inUse").getBoolean(true)) {

                powerCellArray = getVisionTable().getSubTable("Power_Cell5").getEntry("values")
                    .getDoubleArray(new double[7]);

                values = new ArrayList<Double>();
                for (int i = 0; i < 7; i++) {

                  values.add(powerCellArray[i]);

                }

                visionArray.set(5, values);

                if (getVisionTable().getSubTable("Power_Cell6").getEntry("inUse").getBoolean(true)) {

                  powerCellArray = getVisionTable().getSubTable("Power_Cell6").getEntry("values")
                      .getDoubleArray(new double[7]);

                  values = new ArrayList<Double>();
                  for (int i = 0; i < 7; i++) {

                    values.add(powerCellArray[i]);

                  }

                  visionArray.set(6, values);

                  if (getVisionTable().getSubTable("Power_Cell7").getEntry("inUse").getBoolean(true)) {

                    powerCellArray = getVisionTable().getSubTable("Power_Cell7").getEntry("values")
                        .getDoubleArray(new double[7]);

                    values = new ArrayList<Double>();
                    for (int i = 0; i < 7; i++) {

                      values.add(powerCellArray[i]);

                    }

                    visionArray.set(7, values);

                    if (getVisionTable().getSubTable("Power_Cell8").getEntry("inUse").getBoolean(true)) {

                      powerCellArray = getVisionTable().getSubTable("Power_Cell8").getEntry("values")
                          .getDoubleArray(new double[7]);

                      values = new ArrayList<Double>();
                      for (int i = 0; i < 7; i++) {

                        values.add(powerCellArray[i]);

                      }

                      visionArray.set(8, values);

                      if (getVisionTable().getSubTable("Power_Cell9").getEntry("inUse").getBoolean(true)) {

                        powerCellArray = getVisionTable().getSubTable("Power_Cell9").getEntry("values")
                            .getDoubleArray(new double[7]);

                        values = new ArrayList<Double>();
                        for (int i = 0; i < 7; i++) {

                          values.add(powerCellArray[i]);

                        }

                        visionArray.set(9, values);

                      }
                    } //End 9
                  } //End 8
                } //End 7
              } //End 6
            } //End 5
          } //End 4
        } //End 3
      } //End 2
    } //End 1
    //End if statement

    //}

    return visionArray;

  }

  public ArrayList<ArrayList<Double>> getGoalArray() {

    ArrayList<ArrayList<Double>> visionArray = new ArrayList<ArrayList<Double>>(1); //We gotta initialize something in each spot

    // Add the table(s) to the master array
    visionArray.add(new ArrayList<Double>());


    // Start if statement
    if (getVisionTable().getSubTable("Goal0").getEntry("inUse").getBoolean(false)) {

      double goalArray[] = getVisionTable().getSubTable("Goal0").getEntry("values").getDoubleArray(new double[7]);

      ArrayList<Double> values = new ArrayList<Double>();

      for (int i = 0; i < 7; i++) {

        values.add(goalArray[i]);

      }

      visionArray.set(0, values);
    }
    return visionArray;
  }

}