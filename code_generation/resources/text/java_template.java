/*----------------------------------------------------------------------------*/
/* Copyright (c) 2018 FIRST. All Rights Reserved.                             */
/* Open Source Software - may be modified and shared by FRC teams. The code   */
/* must be accompanied by the FIRST BSD license file in the root directory of */
/* the project.                                                               */
/*----------------------------------------------------------------------------*/

package frc.robot.subsystems;

import edu.wpi.first.networktables.NetworkTable;
import edu.wpi.first.networktables.NetworkTableEntry;
import edu.wpi.first.networktables.NetworkTableInstance;
import edu.wpi.first.wpilibj.command.Subsystem;
import frc.robot.commands.FaceTowards;

/**
 * Data structure for returned arrays is as follows: - Each column (first value)
 * represents a space to store object values The data structure of the rows is
 * as follows: - 0 or -1, with -1 being not used and 0 being used (meaning data
 * is valid and should be considered) - centerX - the x cordinate of the center
 * - centerY - the y cordinate of the center - endX - the x cordinate of the
 * bottom right corner of the bounding box - endY - the y cordinate of the
 * bottom right corner of the counding box - area - the area of the bounding box
 * - confidence - the confidence level of the neural network that the object is
 * indeed what it is tagged as
 */
public class EVSNetworkTables extends Subsystem {
  // Put methods for controlling this subsystem
  // here. Call these from Commands.
  String inUse = "inUse";
  String values = "values";

  NetworkTableInstance n = NetworkTableInstance.getDefault();
  NetworkTable evs;

  // Create and assign hatch tables
  NetworkTable hatch0;
  NetworkTable hatch1;
  NetworkTable hatch2;

  NetworkTableEntry hatch_inUse0;
  NetworkTableEntry hatch_values0;

  NetworkTableEntry hatch_inUse1;
  NetworkTableEntry hatch_values1;

  NetworkTableEntry hatch_inUse2;
  NetworkTableEntry hatch_values2;

  // Create and assign ball values
  NetworkTable ball0;
  NetworkTable ball1;
  NetworkTable ball2;

  NetworkTableEntry ball_inUse0;
  NetworkTableEntry ball_values0;

  NetworkTableEntry ball_inUse1;
  NetworkTableEntry ball_values1;

  NetworkTableEntry ball_inUse2;
  NetworkTableEntry ball_values2;

  // Create and assign ball values
  /*NetworkTable tape0 = evs.getSubTable("Tape0");
  NetworkTable tape1 = evs.getSubTable("Tape1");
  NetworkTable tape2 = evs.getSubTable("Tape2");
  NetworkTable tape3 = evs.getSubTable("Tape3");
  NetworkTable tape4 = evs.getSubTable("Tape4");
  NetworkTable tape5 = evs.getSubTable("Tape5");

  NetworkTableEntry tape_inUse0;
  NetworkTableEntry tape_values0;

  NetworkTableEntry tape_inUse1;
  NetworkTableEntry tape_values1;

  NetworkTableEntry tape_inUse2;
  NetworkTableEntry tape_values2;

  NetworkTableEntry tape_inUse3;
  NetworkTableEntry tape_values3;

  NetworkTableEntry tape_inUse4;
  NetworkTableEntry tape_values4;

  NetworkTableEntry tape_inUse5;
  NetworkTableEntry tape_values5;
*/
  @Override
  public void initDefaultCommand() {
    // Set the default command for a subsystem here.
    // setDefaultCommand(new MySpecialCommand());

  }

  public void getVisionNetworkTable() {

    n = NetworkTableInstance.getDefault();
    evs = n.getTable("EVS");

    hatch0 = evs.getSubTable("Hatch0");
    hatch1 = evs.getSubTable("Hatch1");
    hatch2 = evs.getSubTable("Hatch2");

    ball0 = evs.getSubTable("Ball0");
    ball1 = evs.getSubTable("Ball1");
    ball2 = evs.getSubTable("Ball2");

  }


  public double[][] getAllObjects() {

    double[][] allValues = new double[12][7];
    return allValues;

  }


  public double[][] getHatches() {
    getVisionNetworkTable();

    hatch_inUse0 = hatch0.getEntry(inUse);
    hatch_values0 = hatch0.getEntry(values);

    hatch_inUse1 = hatch1.getEntry(inUse);
    hatch_values1 = hatch1.getEntry(values);

    hatch_inUse2 = hatch2.getEntry(inUse);
    hatch_values2 = hatch2.getEntry(values);

    double[][] hatchValues = new double[3][7];

    // if inUse is true, store values and check next table
    if (hatch_inUse0.getBoolean(false) == true) {
      double hatch0_values_array[] = hatch_values0.getDoubleArray(new double[6]);

      for (int i = 0; i < 7; i++) {
        if (i == 0) {
          hatchValues[0][i] = 0;
        } else {
          hatchValues[0][i] = hatch0_values_array[i - 1];
        }

      }

      if (hatch_inUse1.getBoolean(false) == true) {

        double hatch1_values_array[] = hatch_values1.getDoubleArray(new double[6]);

        for (int i = 0; i < 7; i++) {
          if (i == 0) {
            hatchValues[1][i] = 0;
          } else {
            hatchValues[1][i] = hatch1_values_array[i - 1];
          }
        }

        if (hatch_inUse2.getBoolean(false) == true) {

          double hatch2_values_array[] = hatch_values2.getDoubleArray(new double[6]);

          for (int i = 0; i < 7; i++) {
            if (i == 0) {
              hatchValues[2][i] = 0;
            } else {
              hatchValues[2][i] = hatch2_values_array[i - 1];
            }
          }
        } else {
          hatchValues[2][0] = -1;
        }

      } else {
        hatchValues[1][0] = -1;
        hatchValues[2][0] = -1;
      }

    } else {
      hatchValues[0][0] = -1;
      hatchValues[1][0] = -1;
      hatchValues[2][0] = -1;
    }

    return hatchValues;

  }

  public double[][] getBalls() {
    getVisionNetworkTable();

    ball_inUse0 = ball0.getEntry(inUse);
    ball_values0 = ball0.getEntry(values);

    ball_inUse1 = ball1.getEntry(inUse);
    ball_values1 = ball1.getEntry(values);

    ball_inUse2 = ball2.getEntry(inUse);
    ball_values2 = ball2.getEntry(values);

    double[][] ballValues = new double[3][7];

    // if inUse is true, store values and check next table
    if (ball_inUse0.getBoolean(false) == true) {
      double ball0_values_array[] = ball_values0.getDoubleArray(new double[6]);

      for (int i = 0; i < 7; i++) {
        if (i == 0) {
          ballValues[0][i] = 0;
        } else {
          ballValues[0][i] = ball0_values_array[i - 1];
        }

      }

      if (ball_inUse1.getBoolean(false) == true) {

        double ball1_values_array[] = ball_values1.getDoubleArray(new double[6]);

        for (int i = 0; i < 7; i++) {
          if (i == 0) {
            ballValues[1][i] = 0;
          } else {
            ballValues[1][i] = ball1_values_array[i - 1];
          }
        }

        if (ball_inUse2.getBoolean(false) == true) {

          double ball2_values_array[] = ball_values2.getDoubleArray(new double[6]);

          for (int i = 0; i < 7; i++) {
            if (i == 0) {
              ballValues[2][i] = 0;
            } else {
              ballValues[2][i] = ball2_values_array[i - 1];
            }
          }
        } else {
          ballValues[2][0] = -1;
        }

      } else {
        ballValues[1][0] = -1;
        ballValues[2][0] = -1;
      }

    } else {
      ballValues[0][0] = -1;
      ballValues[1][0] = -1;
      ballValues[2][0] = -1;
    }

    return ballValues;

  }
/*
  public double[][] getTape() {

    tape_inUse0 = tape0.getEntry(inUse);
    tape_centerX0 = tape0.getEntry(centerX);
    tape_centerY0 = tape0.getEntry(centerY);
    tape_endX0 = tape0.getEntry(endX);
    tape_endY0 = tape0.getEntry(endY);
    tape_area0 = tape0.getEntry(area);
    tape_confidence0 = tape0.getEntry(confidence);

    tape_inUse1 = tape1.getEntry(inUse);
    tape_centerX1 = tape1.getEntry(centerX);
    tape_centerY1 = tape1.getEntry(centerY);
    tape_endX1 = tape1.getEntry(endX);
    tape_endY1 = tape1.getEntry(endY);
    tape_area1 = tape1.getEntry(area);
    tape_confidence1 = tape1.getEntry(confidence);

    tape_inUse2 = tape2.getEntry(inUse);
    tape_centerX2 = tape2.getEntry(centerX);
    tape_centerY2 = tape2.getEntry(centerY);
    tape_endX2 = tape2.getEntry(endX);
    tape_endY2 = tape2.getEntry(endY);
    tape_area2 = tape2.getEntry(area);
    tape_confidence2 = tape2.getEntry(confidence);

    tape_inUse3 = tape3.getEntry(inUse);
    tape_centerX3 = tape3.getEntry(centerX);
    tape_centerY3 = tape3.getEntry(centerY);
    tape_endX3 = tape3.getEntry(endX);
    tape_endY3 = tape3.getEntry(endY);
    tape_area3 = tape3.getEntry(area);
    tape_confidence3 = tape3.getEntry(confidence);

    tape_inUse4 = tape4.getEntry(inUse);
    tape_centerX4 = tape4.getEntry(centerX);
    tape_centerY4 = tape4.getEntry(centerY);
    tape_endX4 = tape4.getEntry(endX);
    tape_endY4 = tape4.getEntry(endY);
    tape_area4 = tape4.getEntry(area);
    tape_confidence4 = tape4.getEntry(confidence);

    tape_inUse5 = tape5.getEntry(inUse);
    tape_centerX5 = tape5.getEntry(centerX);
    tape_centerY5 = tape5.getEntry(centerY);
    tape_endX5 = tape5.getEntry(endX);
    tape_endY5 = tape5.getEntry(endY);
    tape_area5 = tape5.getEntry(area);
    tape_confidence2 = tape5.getEntry(confidence);

    double[][] tapeValues = new double[6][7];
    // if inUse is true, store values and check next table

    if (tape_inUse0.getBoolean(false) == true) {

      tapeValues[0][0] = 0;
      tapeValues[0][1] = tape_centerX0.getDouble(-1);
      tapeValues[0][2] = tape_centerY0.getDouble(-1);
      tapeValues[0][3] = tape_endX0.getDouble(-1);
      tapeValues[0][4] = tape_endY0.getDouble(-1);
      tapeValues[0][5] = tape_area0.getDouble(-1);
      tapeValues[0][6] = tape_confidence0.getDouble(-1);

      if (tape_inUse1.getBoolean(false) == true) {

        tapeValues[1][0] = 0;
        tapeValues[1][1] = tape_centerX1.getDouble(-1);
        tapeValues[1][2] = tape_centerY1.getDouble(-1);
        tapeValues[1][3] = tape_endX1.getDouble(-1);
        tapeValues[1][4] = tape_endY1.getDouble(-1);
        tapeValues[1][5] = tape_area1.getDouble(-1);
        tapeValues[1][6] = tape_confidence1.getDouble(-1);

        if (tape_inUse2.getBoolean(false) == true) {

          tapeValues[2][0] = 0;
          tapeValues[2][1] = tape_centerX2.getDouble(-1);
          tapeValues[2][2] = tape_centerY2.getDouble(-1);
          tapeValues[2][3] = tape_endX2.getDouble(-1);
          tapeValues[2][4] = tape_endY2.getDouble(-1);
          tapeValues[2][5] = tape_area2.getDouble(-1);
          tapeValues[2][6] = tape_confidence2.getDouble(-1);

          if (tape_inUse3.getBoolean(false) == true) {

            tapeValues[3][0] = 0;
            tapeValues[3][1] = tape_centerX3.getDouble(-1);
            tapeValues[3][2] = tape_centerY3.getDouble(-1);
            tapeValues[3][3] = tape_endX3.getDouble(-1);
            tapeValues[3][4] = tape_endY3.getDouble(-1);
            tapeValues[3][5] = tape_area3.getDouble(-1);
            tapeValues[3][6] = tape_confidence3.getDouble(-1);

            if (tape_inUse3.getBoolean(false) == true) {

              tapeValues[3][0] = 0;
              tapeValues[3][1] = tape_centerX3.getDouble(-1);
              tapeValues[3][2] = tape_centerY3.getDouble(-1);
              tapeValues[3][3] = tape_endX3.getDouble(-1);
              tapeValues[3][4] = tape_endY3.getDouble(-1);
              tapeValues[3][5] = tape_area3.getDouble(-1);
              tapeValues[3][6] = tape_confidence3.getDouble(-1);

              if (tape_inUse4.getBoolean(false) == true) {

                tapeValues[4][0] = 0;
                tapeValues[4][1] = tape_centerX4.getDouble(-1);
                tapeValues[4][2] = tape_centerY4.getDouble(-1);
                tapeValues[4][3] = tape_endX4.getDouble(-1);
                tapeValues[4][4] = tape_endY4.getDouble(-1);
                tapeValues[4][5] = tape_area4.getDouble(-1);
                tapeValues[4][6] = tape_confidence4.getDouble(-1);

                if (tape_inUse5.getBoolean(false) == true) {

                  tapeValues[5][0] = 0;
                  tapeValues[5][1] = tape_centerX5.getDouble(-1);
                  tapeValues[5][2] = tape_centerY5.getDouble(-1);
                  tapeValues[5][3] = tape_endX5.getDouble(-1);
                  tapeValues[5][4] = tape_endY5.getDouble(-1);
                  tapeValues[5][5] = tape_area5.getDouble(-1);
                  tapeValues[5][6] = tape_confidence5.getDouble(-1);

                } else {
                  tapeValues[5][0] = -1;
                }

              } else {
                tapeValues[4][0] = -1;
                tapeValues[5][0] = -1;
              }

            } else {
              tapeValues[3][0] = -1;
              tapeValues[4][0] = -1;
              tapeValues[5][0] = -1;
            }
          } else {
            tapeValues[3][0] = -1;
            tapeValues[4][0] = -1;
            tapeValues[5][0] = -1;

          }
        } else {
          tapeValues[2][0] = -1;
          tapeValues[3][0] = -1;
          tapeValues[4][0] = -1;
          tapeValues[5][0] = -1;
        }

      } else {
        tapeValues[1][0] = -1;
        tapeValues[2][0] = -1;
        tapeValues[3][0] = -1;
        tapeValues[4][0] = -1;
        tapeValues[5][0] = -1;
      }

    }

    else {
      tapeValues[0][0] = -1;
      tapeValues[1][0] = -1;
      tapeValues[2][0] = -1;
      tapeValues[3][0] = -1;
      tapeValues[4][0] = -1;
      tapeValues[5][0] = -1;
    }

    return tapeValues;

  }
*/
}