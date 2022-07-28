# Riflelytics
## Table of Contents
1. [Introduction](#introduction)
2. [Functions](#functions)
   1. [Api](#functions_api)
   2. [Auth](#functions_auth)
   3. [Plotsheet](#functions_plotsheet)
   4. [Profile](#functions_profile)

<a name="introduction"></a>
## Introduction
Riflelytics provides Australian rifle shooters with access to a digital record of their shooting history at 
[riflelytics.com](https://www.riflelytics.com/). It is based off the Flask framework.


-- Created by Ryan Tan, Henry Guo, Dylan Huynh and Rishi Wig

<a name="functions"></a>
## Functions

<a name="functions_api"></a>
### Api
| Function Name            | Description                                                                                                                            | Parameters                                                    | Output                                                                                                                                                                                                                                      |
|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| /submit_notes            | POST<br/>Adds the given notes to the databse                                                                                           | [stageId: integer, <br/>fieldVal: string]                     | {success: 'success'}                                                                                                                                                                                                                        |
| /get_avg_shot_graph_data | POST<br/>Collect shots for use in the averages/standard dev line graph                                                                 | userId: integer                                               | {scores: int[], times: int[], sd: int[]}                                                                                                                                                                                                    |
| /get_users               | POST<br/>Generates a list of names used to complete the autofill fields. Used in autofill.js <br/><br/> Returns a list of dictionaries |                                                               | List of {label: string, value: string}                                                                                                                                                                                                      |
| /get_shots               | POST<br/>Collect shots for use in the recent shots cards                                                                               | [userId: int,<br/>numLoaded: int,<br/>dateRange: string]      | {scores: stage.format_shots()['scores'],<br/> totalScore: string, <br/> groupSize: int, <br/> distance: string, <br/> timestamp: '%d %b %Y %I:%M %p', <br/> std: int, <br/> duration: UNKNOWN, <br/> stageId: int, <br/> sighters: UNKNOWN} |
| /get_target_stats        | POST<br/>Provides database information for ajax request in ajax_target.js<br/>MAY BE REDUNDANT                                         | stageId: integer                                              | {success: 'success'} &#124; {error: 'userID'}                                                                                                                                                                                               |
| /get_all_shots_season    | POST<br/>Collects every shot in the time-frame selected by the user                                                                    | {distance: string,<br/> userID: int, <br/> dateRange: string} | {target, <br/> boxPlot: int[], <br/> bestStage: {id: int, score: int, time: string}, <br/> worstStage: {id: int, score: int, time: string}}                                                                                                 |
| /submit_table            | POST<br/>Updates a user object(given by ID) with the new information provided in the user profile table                                | [userId: int, dictionary of table fields]                     | {success: 'success'}                                                                                                                                                                                                                        |

<a name="functions_auth"></a>
### Auth
auth

<a name="functions_plotsheet"></a>
### PlotSheet
PlotSheet
<a name="functions_profile"></a>

### Profile
Profile

### User

| Function          | Description                                                                                                                                     | Parameters                                                    | Output                                                                         |
|-------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------|--------------------------------------------------------------------------------|
| generate_username | Generates unique username and appends it to user.username                                                                                       | user: User(self) <br/> user.fName, user.sName must be defined | N/A                                                                            |
| get_school_year   | Determines the user's school year based on their graduation year and current year                                                               | user: User(self) <br/> user.gradYr must be defined            | On Success <br/>     int: gradYr <br/>Excepts Error if<br/>GradYr is undefined |
| season_stats      | Returns {mean, median, std, groupSize, duration} of a shooter at a specific distance. If no stages are found all the about fields will equal 0. | user: User(self) <br/> distance: string                       | On Success <br/> {mean, median, std, groupSize, duration}                      |
|                   |                                                                                                                                                 |                                                               |                                                                                |
|                   |                                                                                                                                                 |                                                               |                                                                                |

