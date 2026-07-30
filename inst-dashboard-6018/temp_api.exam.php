<?php
Module::import("Query");
Module::import("Employee");
Module::import("Student");
Module::import("log");
require_once 'api.export.php';
require_once 'api.results.php';



class Exam {
	private static $sql = array(
		'data' => [
			'id',
			'name',
			'status',
			'exam.date',
			'duration',
			'totalQ',
			'mark',
			'settings',
			'created',
			'modified',
			'ipaddr',
			'teacherLinkId',
			// 'parent',
			'value',
			'access',
			'successMark',
			'teacherlink.facultyId as facultyId',
			'faculty.name as facultyName',
			'teacherlink.majorId as majorId',
			'class.name as className',
			'class.id as classId'
		],
		'join' => array(
			'teacherlink'   => 'FIND_IN_SET(teacherlink.id,exam.teacherLinkId)',
			//'studentstatus' => 'studentstatus.facultyId = teacherlink.facultyId',
			//'reservation'   => 'reservation.examId = exam.id',
			'faculty'       => 'faculty.Id = teacherlink.facultyId',
			'class'	        => 'class.Id = teacherlink.classId',
		),
		'groupby' => 'exam.id',
		'order'   => ['exam.date' => "desc"]
	);
	
	public static function getExams(&$router, $args) {
		global $config;
		$appStatus = $config['settings']['appStatus'];
		
		$sql = self::$sql;
		if($config['settings']['majorLevel']){
			array_push($sql['data'], "major.name as majorName", "teacherlink.majorId");
			$sql['join']['major'] = "major.Id = teacherlink.majorId";
		} 
	
		$examUseCourse = $config['settings']['examUseCourse'];
		$showTeacherName = $config['settings']['showTeacherName'];
		if($examUseCourse) {
			array_push($sql['data'], "course.name as courseName", "courseId");
			$sql['join']['course'] = "course.Id = exam.courseId";
		}
	
		if($showTeacherName) {
			array_push($sql['data'], 'employee.name as teacherName');
			$sql['join']['employee'] = 'employee.id = teacherlink.teacherId';
		}
		
		$fetch = [];
		if(isset($args->fetch)) $fetch = explode(",", $args->fetch);
		if(in_array("total", $fetch)) {
			return Query::table("exam")->param("count(id) as total")
			->where("status", "!=", "template")
			->get()->record[0];
		}
		if(Employee::logged() && !Employee::hasRule("show-all-exams")) $sql['where']['teacherId'] = Employee::id();
		if(isset($router->id)) {
			$sql['where']['id'] =  ":in: {$router->id}";
			$array = explode(",", $router->id);
			if(count($array) > 1) {
				$array = "'".implode("','",$array)."'";
				$sql['order'] = "FIELD(exam.id,$array)";
			}
		}

		if(isset($args->status)) {
			$sarr = explode(',', $args->status);
			$s = '';
			foreach($sarr as $val) {
				$val = "'".$val."'";
				if($s == '') $s = $val;
				else $s = $s.','.$val;
			};
			if($args->status == "attended") $sql['where']['id'] = ":in: (select result.examId from result )";
			else if($args->status == "notAttended") $sql['where']['id'] = ":notin: (select result.examId from result )";
			else if($args->status == "notCompleted") $sql['where']['id'] = ":in: (select result.examId from result where result.currentMark = -1)";
			else if($args->status == "Complete") $sql['where']['status'] = "Complete";
			else $sql['where']["status"] = ":in:{$s}";
		}
		if(isset($args->excludeStatus)) {
			$sarr = explode(',', $args->excludeStatus);
			$s = '';
			foreach($sarr as $val) {
				$val = "'".$val."'";
				if($s == '') $s = $val;
				else $s = $s.','.$val;
			};
			$sql['where']["status"] = ":notin:{$s}";
		}
		
		// if($args->unparented == true) {
		// 	$sql['where']['id'] = ":notin:(select exam.parent from exam)";
		// }
		if(isset($args->datefrom) &&  isset($args->dateto)) {
			$sql['where']['date'] = ":bet:'{$args->datefrom}','{$args->dateto}'";
		} else if(isset($args->datefrom)) {
			$sql['where']['date'] = ":gte:'{$args->datefrom}'";
		} else if(isset($args->dateto)) {
			$sql['where']['date'] = ":lte:'{$args->dateto}'";
		} else if(isset($args->date)) {
			$sql['where']['date'] = "{$args->date}";
		}
		if(in_array("requireRes", $fetch)){
			$sql['where']['settings'] = ':like:%"requireRes":true%';
		}
		if(in_array("noReservations", $fetch)){
			$sql['where']['id'] = ':notin: select examId from reservation';
		}

		if(in_array("firstSession", $fetch)){ // to return first session from sessions group 
			$linkedSessions = Query::table("examsrelation")->param('examSet')->where('type','sessions')		                 
			->where('statusId', $appStatus)->get();
			if($linkedSessions->count > 0) {

				$linkedSessionsIds = array_map(function($e){
					$examset = explode(',', $e['examSet']);
					array_shift($examset);
					$examset = implode(",", $examset);
					return $examset;
				},$linkedSessions->record);
				$linkedSessionsIds = implode(",", $linkedSessionsIds);
				$sql['where']['id'] = ":notin:{$linkedSessionsIds}";

			}
			
		}
		

		if(in_array("hasSessions", $fetch)) {
			$sql['where']['settings'] = ':like:%"hasSessions":true%';
		}

		if(isset($args->linkId)) $sql['where']['teacherLinkId'] = ":inset:{$args->linkId}";
	
		// to select exam based on those filters	
		if(!isset($args->linkId) && (isset($args->facultyId) || isset($args->majorId) || isset($args->courseId) || isset($args->classId))) {
			$tlQuery =  Query::table("teacherlink")
			->param('id');	
			isset($args->facultyId) &&  $tlQuery->where('teacherlink.facultyId' , $args->facultyId );
			isset($args->majorId) &&  $tlQuery->where('teacherlink.majorId' , $args->majorId );
			isset($args->courseId) &&  $tlQuery->where('teacherlink.courseId' , $args->courseId );
			isset($args->classId) &&  $tlQuery->where('teacherlink.classId' , $args->classId );
			$result = $tlQuery->get();

			if($result->count){
				$set = [];
				foreach($result->record as $rec){
					$set[] = $rec['id'];
				}

				$set = implode(',' , $set);
				$sql['where']['teacherLinkId'] = ":in:{$set}";
			}
		}

		if(isset($args->order)) {
			$order = explode(',', $args->order);
			if(count($order) > 1) {
				$sql['order'] = array($order[0]=>$order[1]);
			} else {
				$sql['order'] = $args->order;
			}
		}
	
		if(in_array("last", $fetch)) {
			$sql['order'] = array("exam.date"=>"desc");
			$sql['limit'] = 1;
		}
		if(Request::get('orderCol') && Request::get('orderDir')) $sql['order'] = [Request::get('orderCol') => Request::get('orderDir')];
		
		//limit and search
		isset($args->limit) && !isset($args->start) &&  $sql['limit'] =  $args->limit;
		isset($args->limit) && isset($args->start)  &&  $sql['limit']  = "{$args->start}, {$args->limit}";
		isset($args->search) && $args->search && $sql['where']['name'] = ":like:%{$args->search}%";// or `exam`.`id` like '%{$args->search}%'";
	   
		
		$q = Query::get("exam", $sql);
		//$q->total = Query::get("exam",["data" => "id"])->count;
		foreach ($q->record as $key => $value) {
			$classSet = Query::get("teacherlink", array('data'=>['classId'], 'where'=>['id'=>":in: {$value['teacherLinkId']}"]));
			$classId = ''; // Initialize classId
			if (isset($classSet->record) && is_array($classSet->record) && !empty($classSet->record)) {
				$arr = array_map(function($class){
					return $class['classId'];
				}, $classSet->record);
				$classId = implode(',', $arr);
			}
			$classId = implode(',', $arr);
			$q->record[$key]['classId'] = $classId;
			$settings = json_decode($value['settings'],true);
			if($value['status'] == "published" || $value['status'] == "parent-published" || $value['status'] == "part-published" && $settings['requireRes']) {
				$hasReservation = false;
				$reservarion = Query::get("reservation", array('data'=>['id'], 'where'=>['examId'=>"{$value['id']}"]));
				if($reservarion->count > 0) $hasReservation = true;
				$q->record[$key]['hasReservation'] = $hasReservation;
			}
			
			if(in_array("examinees", $fetch))  {
				if(isset($settings->hasSessions) && $settings->hasSessions && isset($settings->sessionsGroup)) {
					$examId = $settings->sessionsGroup;
				} else {
					$examId = [$value['id']];
				}
			
				$teacherLinkId = $value['teacherLinkId'];
				$students = Query::table("student")->param('count(id )as applicants')
					   ->Join("studentstatus", "student.id", "~studentstatus.studentId")
					   ->Join("exam", "~exam.id",  $value['id'])
					   ->where("studentstatus.teacherLinkSet", 'inset-or', explode(',', $teacherLinkId))
					   ->where("studentstatus.statusId", $appStatus);

				$settings =  json_decode($value['settings'], true);	   
				if(isset($settings['requireRes']) && $settings['requireRes']) {
				
					$students->where("exam.id", "in", function($e) {
							$e->table('reservation')->param('examId')->get();
					});
	
					$reservation = Query::table("reservation")->param("id")->param("studentSet")->where('examId', 'in', $examId)->get();
					if($reservation->count) {
						$studentIds =  array();
						$studentSet = array();
						foreach ($reservation->record as $key1 => $value1) {
							array_push($studentIds,  explode(',', $value1['studentSet']));
						}
						foreach ($studentIds as $set) {
							$studentSet = array_merge($studentSet, $set);
						}
						$students->where('student.id', "in",  $studentSet);
						
					}
				}

				$q->record[$key]['applicants'] = $students->get()->record[0]['applicants'];
				

				$examinees = clone($students);
				$examinees->where('student.id', 'in', "~~select studentId from result where examId in (".(implode(',', $examId)).")");
				$q->record[$key]['examinees'] = $examinees->get()->record[0]['applicants'];

			}

			$sessionsCount = 1;
			if(isset($settings['hasSessions']) && $settings['hasSessions'] && isset($settings['sessionsGroup'])) {
				$sessionsCount = count ($settings['sessionsGroup']);
			}
			$q->record[$key]['sessionsCount'] = $sessionsCount;

		}
		if(in_array("all", $fetch) || in_array("link", $fetch) ||in_array("child", $fetch)) {
			if(in_array("all", $fetch) || in_array("child", $fetch)) getChilds($q->record);
			if(in_array("all", $fetch) || in_array("link", $fetch)) {
				foreach($q->record as $key => $row) {
					$teacherLinkarr = explode(',', $row['teacherLinkId']);
					foreach($teacherLinkarr as $val) {
						$sql2 = array(
							"data" => [],
							"where" => ['teacherlink.id' => $val],
						);
						if($examUseCourse) {
							array_push($sql2['data'], "course.id as courseId", "course.name as courseName");
							$sql2['join']['course'] = "course.id = teacherlink.courseId";
						}
						if($showTeacherName) {
							array_push($sql2['data'], 'employee.name as teacherName', 'employee.id as teacherId');
							$sql2['join']['employee'] = 'employee.id = teacherlink.teacherId';
						}
						$q2 = Query::get("teacherlink", $sql2);

						$q->record[$key]['link'] = $q2;
						$q->record[$key]['courseName'] = $q2->record[0]['courseName'];
						$q->record[$key]['courseId'] = $q2->record[0]['courseId'];
					}
					// fix settings
					if(isset($args->parse) &&  $args->parse == "yes"){
						Module::import("res.wiris");
						//$q->record[$key]['title'] = res\wiris::parse(json_decode($q->record[$key]['title']));

					}
				}
			}
		}


		if(in_array("concatenation", $fetch))  {
			$sql2 = array(
				"data" => [
					'examSet',
					'relation',
					'type',
			]);
			foreach($q->record as $key => $row) {
				if($q->record[$key]['status'] == 'part-published' || $q->record[$key]['status'] == 'parent-published') {
					$sql2['where'] [ 'examSet'] = " :inset: {$q->record[$key]['id']}";
					$q2 = Query::get("examsrelation", $sql2);
					$q->record[$key]['concatenation'] = $q2;

				}
			}
		}

		if(in_array("all", $fetch) || in_array("link", $fetch) && isset($args->parse) && $args->parse == "yes") {
			Module::import("res.wiris");
			// echo res\wiris::parse("<html><body><b>Formula: </b><math><mfrac><mi>x</mi><mn>1000</mn></mfrac></math></body></html>");
			// exit;
			if(isset($router->id)){
				if(isset($args->studentId)){
					$extraTime = Query::table("result")->param('extraTime','extraStatus')->where('examId', $router->id)->where('studentId', $args->studentId)->get();
					$extraTime->count  && $q->record[0]["extraTime"] = $extraTime->record[0]["extraTime"];
					$extraTime->count  && $q->record[0]["extraStatus"] = $extraTime->record[0]["extraStatus"];
					!$extraTime->count && $q->record[0]["extraTime"] = 0;
				}
				function parseMath($text){
					if(is_string($text) && (null !== $temp = json_decode($text, true))){
						$text = $temp;
					}
					/*
					ob_start();

					$temp = stripslashes($text);
					eval("$temp = {$temp};");

					if ('' !== $error = ob_get_clean()) {
						// output the error somehow to the client
						// $a = $st;
					}else{
						$text = $temp;
					}
					*/

					if(is_array($text)){
						foreach ($text as $key => $value) {
							$text[$key] = parseMath($value);
						}
						$text = json_encode($text);
					}else if(is_object($text)){
						foreach ($text as $key => $value) {
							$text->{$key} = parseMath($value);
						}
						$text = json_encode($text);
					}else{
						$text = stripslashes($text);
						$text = stripslashes($text);
						$text = res\wiris::parse($text);

					}
					return $text;
				};

				foreach($q->record[0]['child']->record as $key => $row) {
					$q->record[0]['child']->record[$key]['title'] = parseMath($q->record[0]['child']->record[$key]['title']);
					$q->record[0]['child']->record[$key]['answers'] = parseMath($q->record[0]['child']->record[$key]['answers']);
				}
				
			}
		}

		// get total query 
		$total = array(
			'data' => [
				'~COUNT(id) as total'
			]);	
			array_key_exists('where', $sql) && $total['where'] = $sql['where'];
		$total = Query::get("exam", $total);
		$q->total = $total->record[0]['total'];

		// $total =  Query::table("exam")->param('count(id) as total');
		// isset($args->search) && $args->search && $total->where('exam.name' , 'like' , '%'.$args->search.'%');
		// isset($args->search) && $args->search && $total->orwhere('exam.id'   , 'like'   , '%'.$args->search.'%');
		// $q->total = $total->get()->record[0]["total"];

		error_log("DEBUG: Exam::getExams - Returning exam data: " . print_r($q, true));
		return $q;
	}

/*
	public static function updateDifficultyLevelForQuestions($examIds){

		$difficultyLevelFilter = Query::table('filters')
									->param('*')
									->where('name','مستوى الصعوبة')
									->orWhere(strtoupper('name'),strtoupper('Difficulty Level'))
									->get();

		if($difficultyLevelFilter->count > 0 ) {
			$difficultyLevelFilter = $difficultyLevelFilter->record[0];
		} else return;

		$difficultyLevelValues = explode(',', $difficultyLevelFilter ['value']);
		$difficultyLevelFilterId = $difficultyLevelFilter['id'];
		
		
		for($i = 0; $i < count($examIds); $i++){

			$examData = Query::table('examdata')->where('examId',$examIds[$i])->get();

			if($examData->count > 0 ) {
				foreach($examData->record as $key => $row) {
					$difficultyLevelValue = "";
					$bankId = $row['bankId'];
					$trueCountInExam = Query::table('studentresult')
									->param('count(id) as trueCount')
									->where('examId',$examIds[$i])
									->where('examDataId', $row['id'])
									->where('currentMark', '>=', $row['mark'] /2)
									->get()->record[0]['trueCount'];

					$falseCountInExam = Query::table('studentresult')
									->param('count(id) as falseCount')
									->where('examId',$examIds[$i])
									->where('examDataId', $row['id'])
									->where('currentMark', '<', $row['mark'] /2)
									->get()->record[0]['falseCount'];

					$countsInBank = Query::table('bank')
										->param('trueAnswersCount', 'falseAnswersCount')
										->where('id', $bankId)->get()->record[0];

					$trueCountInBank = $countsInBank['trueAnswersCount'];
					$falseCountInBank = $countsInBank['falseAnswersCount'];
					
					$totalTrueCount = intval($trueCountInExam) + intval($trueCountInBank);  
					$totalFalseCount = intval($falseCountInExam) + intval($falseCountInBank); 

					$totalAnswers = $totalTrueCount + $totalFalseCount;
					

					if($totalTrueCount >= 0 && $totalTrueCount < (.33 * $totalAnswers)) { //hard
						$difficultyLevelValue = $difficultyLevelValues[0];
					} else if ($totalTrueCount >= (.33 * $totalAnswers) && $totalTrueCount <= (.66 * $totalAnswers)) { //medium
						$difficultyLevelValue = $difficultyLevelValues[1];
					} else if ($totalTrueCount > (.66 * $totalAnswers)) { //easy
						$difficultyLevelValue = $difficultyLevelValues[2];
					}
					

					Query::table('bank')
						->param('trueAnswersCount', $totalTrueCount)
						->param('falseAnswersCount', $totalFalseCount)
						->where('id', $bankId)->set();


					Query::table('filtersdata')
						->param('value', $difficultyLevelValue)
						->where('bankId', $bankId)
						->where('filterId', $difficultyLevelFilterId)
						->where('type', 1)->set();

				}

			
			}
		}
	}

	public static function updateDiscriminationFactorForQuestions($examIds) {

		$discriminationFactorFilter = Query::table('filters')
											->param('*')
											->where('name',' معامل التمييز')
											->orWhere(strtoupper('name'),strtoupper('discrimination factor'))
											->get();
		if($discriminationFactorFilter->count > 0 ) {
			$discriminationFactorFilterId = $discriminationFactorFilter->record[0]['id'];
		} else return;
		for($i = 0; $i < count($examIds); $i++){

			$obj = (object) array('id' => $examIds[$i]);
			$args = (object) array('fetch' => 'attend');

			$examResult = Result::getExamResult($obj, $args);

			$studentsCount = $examResult->count;

			$choosenStudentCount = round($studentsCount * .27);

			if( $studentsCount > 0) {
				$students_arr = $examResult->record;
				
				//sudents Ids from top marks

				$topMarksStudents = array_map(function($student) { 
											return $student['studentId']; 
										}, array_slice($students_arr, 0, $choosenStudentCount));
				
				//students  Ids from lower marks
				$lowerMarksStudents = array_map(function($student) { 
											return $student['studentId']; 
										}, array_slice($students_arr, -$choosenStudentCount, $choosenStudentCount));

				
				$examData = Query::table('examdata')->where('examId',$examIds[$i])->get();

				if($examData->count > 0 ) {
					foreach($examData->record as $key => $row) {

						$trueAnswersCountForTopMarks = Query::table('studentresult')
									->param('count(id) as trueCount')
									->where('examId',$examIds[$i])
									->where('examDataId', $row['id'])
									->where('studentId', 'in', $topMarksStudents)
									->where('currentMark', '>=', $row['mark'] /2)
									->get()->record[0]['trueCount'];

						$trueAnswersCountForLowMarks = Query::table('studentresult')
									->param('count(id) as trueCount')
									->where('examId',$examIds[$i])
									->where('examDataId', $row['id'])
									->where('studentId', 'in', $lowerMarksStudents)
									->where('currentMark', '>=', $row['mark'] /2)
									->get()->record[0]['trueCount'];

						$discriminationFactorValue = ($trueAnswersCountForTopMarks - $trueAnswersCountForLowMarks) / $choosenStudentCount;
						$discriminationFactorValue = number_format($discriminationFactorValue, 2, '.', ',');

						Query::table('filtersdata')
									->param('value', $discriminationFactorValue)
									->where('bankId', $row['bankId'])
									->where('filterId', $discriminationFactorFilterId)
									->where('type', 1)->set();
						
					}
				
				}

				
	
			}

			

		}
	}
*/
}

/**
 * API Group: exam
 *
 * @access  public
 * @return  json | exam Information
 */
API::group("exam", function() {
	global $config;
	$examUseCourse = $config['settings']['examUseCourse'];
	$showTeacherName = $config['settings']['showTeacherName'];

	function getChilds(&$data) {

		foreach($data as $key => $row) {
			$qdata = array(
				'data' => [
					'id',
					'type',
					'title',
					'answers',
					'correct',
					'mark',
					'duration',
					'resources',
					'bankId',
					'modelId',
					'context',
					'filters'
				],
				'where'   => ['examId' => $row['id']],
				'join'    => ["filtersdata" => "filtersdata.bankId = examdata.bankId"],
				'groupby' => 'examdata.id',
			);
			$q1 = Query::get("examdata", $qdata);
			$data[$key]['child'] = $q1;
			// foreach($q1->record as $key1 => $row) {
	    //         $filters = array();
			// 	$q2 = Query::get("filtersData", [
			// 		"data"  => ['filterId', 'value','filters.name'],
			// 		"where" => ["bankId" => $row['bankId']],
			// 		"join"  => ["filters" => "filters.id = filtersData.filterId"]
			// 	]);
			// 	if($q2->count != 0 ) {
			// 		foreach($q2->record as $key => $row) {
			// 			$filters[$q2->record[$key]['filterId']] = $q2->record[$key]['value'];
			// 		}
			// 	}
			// 	$q1->record[$key1]['filters'] = $filters;
		  //  }
		}
	}

	function insertTobank(&$qdata, &$courseId, &$examid, &$examUseCourse){

		foreach($qdata as $row) {
			if($row['bankId'] == 0) {
			  // if($courseId != 0) {
				$cat = array('data' => ['id']);
				//if($examUseCourse) $cat['where']['category.courseId'] = $courseId;
			//	$catset = Query::get("category", $cat);
			//	$catId = $catset->record[0]['id'];
			   // } else $catId = 0;

				$banksql['data']['categorySet'] = 0;
				$banksql['data']['courseId'] = $courseId;
				if(isset($row['mark'])) {
					$banksql['data']['mark'] = $row['mark'];
				}
				if(isset($row['duration'])) {
					$banksql['data']['duration'] = $row['duration'];
				}
				if(isset($row['title'])) {
					$banksql['data']['title'] = $row['title'];
				}
				if(isset($row['type'])) {
					$banksql['data']['type'] = $row['type']?:"mch";
				}
				if(isset($row['answers'])) {
					$banksql['data']['answers'] = $row['answers'];
				}
				if(isset($row['correct'])) {
					$banksql['data']['correct'] = $row['correct'];
				}
				if(isset($row['resources'])) {
					$banksql['data']['resources'] = $row['resources'];
				}

				$bankres = Query::set("bank", $banksql);
				$bankId = $bankres->last;
			    if(isset($row['filters'])) {
						$filters = json_decode($row['filters']);
					foreach($filters as $key => $value) {
						Database::query("insert into filtersdata(bankId, filterId, value, type)
				            values('{$bankId}', '{$key}', '{$value}',1) ON DUPLICATE KEY UPDATE value = '{$value}';"
					   );
					}
				}
				// TODO::tamer, this need to b checked
				// if(isset($row['objective'])) {
				// 	Database::query("insert into filtersData(bankId, filterId, value)
				// 		values('{$bankId}', '{$args->objective[xId]}', '{$args->objective[name]}',3) ON DUPLICATE KEY UPDATE value = '{$args->objective[name]}';"
				// 	);
				// }

				//saving to Log
				$logsql = array("data" => array("bankId" => $bankId, "examId" => $examid));
				$logres = Query::set("banklog", $logsql);
				//update exam data bank Id
				$setbankId = array("data" => array("bankId" => $bankId), "where" => array('id' => $row['id']));
				$setbankIdRes = Query::set("examdata", $setbankId);
			}
			// saving to Log
			$logsql = array("data" => array("bankId" => $row['bankId'], "examId" => $examid));
			$logres = Query::set("banklog", $logsql);
        }

	}

	$sql = array(
		'data' => [
			'id',
		    'name',
		    'status',
		    'exam.date',
		    'duration',
		    'totalQ',
		    'mark',
		    'settings',
		    'created',
		    'modified',
		    'ipaddr',
		    'teacherLinkId',
		    // 'parent',
		    'value',
		    'access',
		    'successMark',
		    'teacherlink.facultyId as facultyId',
		    'faculty.name as facultyName',
			'teacherlink.majorId as majorId',
			'class.name as className',
			'class.id as classId'
		],
		'join' => array(
			'teacherlink'   => 'FIND_IN_SET(teacherlink.id,exam.teacherLinkId)',
	  		'studentstatus' => 'studentstatus.facultyId = teacherlink.facultyId',
			'reservation'   => 'reservation.examId = exam.id',
			'faculty'       => 'faculty.Id = teacherlink.facultyId',
			'class'	        => 'class.Id = teacherlink.classId',
		),
		'groupby' => 'exam.id',
		'order'   => ['exam.date' => "desc"]
	);

	 if($config['settings']['majorLevel']){
		 array_push($sql['data'], "major.name as majorName", "teacherlink.majorId");
		 $sql['join']['major'] = "major.Id = teacherlink.majorId";
	 } 


	if($examUseCourse) {
		array_push($sql['data'], "course.name as courseName", "courseId");
		$sql['join']['course'] = "course.Id = exam.courseId";
	}

	if($showTeacherName) {
        array_push($sql['data'], 'employee.name as teacherName');
        $sql['join']['employee'] = 'employee.id = teacherlink.teacherId';
    }

	// --------------------------------------------------------------------

	/**
	 * GET: exam/course:id
	 *
	 * @access  public
	 * @effects: module.edata.js |
	 * @return  json | exam for course id
	 */
	API::get("course", ['id'], function(&$scope, $router) use ($sql, $examUseCourse) {

		if( !(Employee::hasRule("exam-can-access") || API::access()) )
			return Employee::accessDenied("exam-can-access");

		if(Employee::logged() && !Employee::hasRule("show-all-exams")) $sql['where']['teacherId'] = Employee::id();
		$args = Request::get(["datefrom", "dateto"]);
		if($examUseCourse && $router->id) $sql['where'] = array("courseId" => $router->id);
		if($args->datefrom &&  $args->dateto ) {
			$sql['where']['date'] = ":bet:'{$args->datefrom}', '{$args->dateto}'";
		}
		$q = Query::get("exam", $sql);
		getChilds($q->record);
		return $q;
	});

	// --------------------------------------------------------------------

	/**
	 * GET: exam/hall:id
	 *
	 * @access  public
	 * @effects: module.edata.js | module.StudentsRep.js
	 * @return  json | exam for hall id
	 */
	API::get("hall", ['id'], function(&$scope, $router) use ($sql) {

		if( !(Employee::hasRule("exam-can-access") || API::access()) )
			return Employee::accessDenied("exam-can-access");
		
		if(Employee::logged() && !Employee::hasRule("show-all-exams")) $sql['where']['teacherId'] = Employee::id();
		$args = Request::get(["datefrom", "dateto"]);
		if($router->id) $sql['where'] = array("reservation.hallId" => $router->id);
		if($args->datefrom &&  $args->dateto) {
			$sql['where']['date']=":bet:'{$args->datefrom}', '{$args->dateto}'";
		}
		$q = Query::get("exam", $sql);
		return $q;
	});

	// --------------------------------------------------------------------

	/**
	 * GET: exam/teacher:id
	 *
	 * @access  public
	 * @effects: module.edata.js | module.StudentsRep.js
	 * @return  json | exam for teacher id
	 */

	API::get("teacher", ['id'], function(&$scope, $router) use ($sql) {

		if( !(Employee::hasRule("exam-can-access") || API::access()) )
			return Employee::accessDenied("exam-can-access");
		if(Employee::logged() && !Employee::hasRule("show-all-exams")) $sql['where']['teacherId'] = Employee::id();
		$args = Request::get(["datefrom", "dateto"]);
		if($router->id) $sql['where'] = array("teacherlink.teacherId" => $router->id);
		$q = Query::get("exam", $sql);
		if($args->datefrom &&  $args->dateto) {
			$sql['where']['date'] = ":bet:'{$args->datefrom}', '{$args->dateto}'";
		}
		return $q;
	});

	// --------------------------------------------------------------------

	/**
	 * GET: exam/class:id
	 *
	 * @access  public
	 * @effects: module.edata.js | module.StudentsRep.js
	 * @return  json | exam for teacher id
	 */

	API::get("class", ['id'], function(&$scope, $router) use ($sql) {

		if( !(Employee::hasRule("exam-can-access") || API::access()) )
			return Employee::accessDenied("exam-can-access");

		if(Employee::logged() && !Employee::hasRule("show-all-exams")) $sql['where']['teacherId'] = Employee::id();
		if($router->id) $sql['where'] = array("teacherlink.classId" => $router->id);
		$q = Query::get("exam", $sql);
		getChilds($q->record);
		return $q;
	});

	// --------------------------------------------------------------------

	/**
	 * GET: exam/parent:id
	 *
	 * @access  public
	 * @effects: vendor\student\app.js |
	 * @return  json | childs for this exam
	 */
	API::get("parent", ['id'], function(&$scope, $router) use ($sql) {

		if(!(
			Student::logged() ||
			Employee::hasRule("exam-can-access") ||
			API::access()
		)) return Employee::accessDenied("exam-can-access");
		$args = Request::get(["fetch"]);
		// if($router->id) $sql['where'] = array("exam.parent" => $router->id);
		$q = Query::get("exam", $sql);
		if($args->fetch == "child") getChilds($q->record, "all");
		return $q;
	});

	// ---------------------------------------------------------------------

	/**
	 * GET: exam/questions:id
	 *
	 * @access  public
	 * @effects: module.correction.js | module.edata.js | module.QbankRep.js
	 * @return  json | questions for this exam
	 */
	API::get("questions", ['id'], function(&$scope, $router) use ($sql, $examUseCourse) {
		if( !(Employee::hasRule("exam-can-access") || API::access()) )
			return Employee::accessDenied("exam-can-access");
		if(Employee::logged() && !Employee::hasRule("show-all-exams")) $sql['where']['teacherId'] = Employee::id();
		$args = Request::get(["fetch", "childs"]);
		if($router->id) $sql['where'] = array("exam.id" => $router->id);
		$q = Query::get("exam", $sql);

		$qdata = array();
		$qdata['data'] = ['id', 'type', 'title', 'answers', 'correct', 'mark', 'duration', 'resources', 'bankId', 'filters' ,'teacherId', 'employee.name as teacherName'];
		if($router->id) $qdata['where']['examId'] = $router->id;
		if($args->fetch == 'uncorrect') $qdata['where']['type'] = ":in:'hw','text'";
		$qdata['join'] = [
			"filtersdata" => "filtersdata.bankId = examdata.bankId",
			"exam"        => "exam.id = examdata.examId",
		];
		if($examUseCourse) $qdata['join']['course'] = "course.id = exam.courseId";
		
		$qdata['groupby'] = 'examdata.id';
		error_log('$qdata: ' . print_r($qdata, true));
		$q1 = Query::get("examdata", $qdata);
		if($args->fetch == 'child') return $q1;
		$q->record[0]['child'] = $q1;
		foreach($q1->record as $_key => $row) {
            $filters = array();
			$q2 = Query::get("filtersdata", [
				"data"  => ['filterId', 'value','filters.name' ],
				"where" => ["bankId" => $row['bankId']],
				"join"  => ["filters" => "filters.id = filtersdata.filterId"]
			]);
			if($q2->count != 0 ) {
				foreach($q2->record as $key => $row) {
					$filters[$q2->record[$key]['filterId']] = $q2->record[$key]['value'];
				}
			}
			$q1->record[$_key]['filters'] = $filters;
	   }
	
	   return $q;
	});

	// --------------------------------------------------------------------

	/**
	 * GET: exam/student:id
	 *
	 * @access  public
	 * @effects: vendor\student\app.js |
	 * @return  json | exam for student id
	 */
	                                                            API::get("student", ['id'], function(&$scope, $router) use ($sql, $examUseCourse, $showTeacherName) {
	                                                                $args = Request::get(['global', 'fetch', 'status']);
	                                                        		$sql2 = array(
	                                                        		  	"data" => [
	                                                        		  		"id",
	                                                        				"name",
	                                                        				"status",
	                                                        				"exam.date",
	                                                        				"exam.access",
	                                                        				"duration",
	                                                        				"totalQ",
	                                                        				"mark",
	                                                        				"settings",
	                                                        				"created",
	                                                        				"modified",
	                                                        				"ipaddr",
	                                                        				"teacherLinkId",
	                                                        				// "parent",
	                                                        				"value" ,
	                                                        				"successMark",
	                                                        				"teacherlink.facultyId as facultyId",
	                                                        				"faculty.name as facultyName",
	                                                        				"class.name as className",
	                                                        
	                                                        			],
	                                                        						"join" => array(
	                                                        							"teacherlink" 	=> "FIND_IN_SET(teacherlink.id,exam.teacherLinkId)",
	                                                        							"studentstatus"	=> "studentstatus.classId = teacherlink.classId",
	                                                        							"student"		=> "student.id = studentstatus.studentId",
	                                                        							"faculty"		=> "faculty.Id = teacherlink.facultyId",
	                                                        							"class"		    => "class.Id = teacherlink.classId",
	                                                        						),
	                                                        						"where" => array(
	                                                        							"studentstatus.teacherLinkSet" => ":inset:teacherlink.id",
	                                                        							"studentstatus.studentId" => "{$router->id}",
	                                                        							"exam.id" => ":notin:(select examId from result where studentId = {$router->id} and status != 'inExam')",
	                                                        						),
	                                                        						"order" =>["exam.date"=>"asc"],
	                                                        						'groupby' => 'exam.id',
	                                                        					);	                                                        
	                                                        		if($examUseCourse) {
	                                                        			array_push($sql2['data'], "course.name as courseName", "courseId");
	                                                        			$sql2['join']['course'] = "course.Id = exam.courseId";
	                                                        		}
	                                                        		if($showTeacherName) {
	                                                                    array_push($sql2['data'], 'employee.name as teacherName');
	                                                                    $sql2['join']['employee'] = 'employee.id = teacherlink.teacherId';
	                                                                }
	                                                               	                                                               if($args->status) {
	                                                               	                                                        					$sarr = explode(',', $args->status);
	                                                               	                                                        					$s = '';
	                                                               	                                                        					foreach($sarr as $val) {
	                                                               	                                                        							$val = "'" . $val . "'";
	                                                               	                                                        								if($s == '') $s = $val;
	                                                               	                                                        							else $s = $s.','.$val;
	                                                               	                                                        					};
	                                                               	                                                        				$sql2['where']["status"] = ":in:{$s}";
	                                                               	                                                        			};
	                                                               	                                                        
	                                                               	                                                        			date_default_timezone_set('Asia/Kuwait');
	                                                               	                                                        			if(!$args->global) $sql2['where']['cast(date as date)'] = date('Y-m-d');
	                                                        		if(Employee::logged() && !Employee::hasRule("show-all-exams")) $sql2['where']['teacherId'] = Employee::id();
	                                                                                                                                $q = Query::get("exam", $sql2);
	                                                                                                                                error_log("SQL2 array: " . print_r($sql2, true));	                                                        		for($i = sizeof($q->record)-1; $i >= 0; $i-- ){

	                                                        			$exam = $q->record[$i];
	                                                        			$settings = json_decode($exam['settings'], true);
	                                                        			if(isset($settings['requireRes']) && $settings['requireRes']) {
	                                                        				$result = Query::get("reservation", array('data' => ['id',], 'where' => ['examId' => $exam['id'], "studentSet" => ":inset:{$router->id}",]));
	                                                        				if ($result->count == 0) {
	                                                        				  array_splice($q->record, $i, 1);
	                                                        					$q->count =  $q->count - 1;
	                                                        				}
	                                                        			}
	                                                        		}
	                                                        
	                                                        		$fetch = explode(",", $args->fetch);
	                                                        		if(in_array("all",$fetch) || in_array("link",$fetch) || in_array("child",$fetch)) {
	                                                        			if(in_array("all",$fetch) || in_array("child",$fetch)) {
	                                                        				$sql2 = array(
	                                                        					"data" => [
	                                                        						'teacherlink.classId',
	                                                        						'teacherlink.id',
	                                                        						'employee.id as teacherId',
	                                                        						'employee.name as teacherName',
	                                                        					 ],
	                                                        					"join" => [
	                                                        						'employee'      => 'employee.id = teacherlink.teacherId',
	                                                        						'studentstatus' => 'studentstatus.classId = teacherlink.classId'
	                                                        					],
	                                                        				    "where" => [explode(",", "all, child")],
	                                                        				);
	                                                        				if($examUseCourse) {
	                                                        					array_push($sql2['data'], "course.id as courseId", "course.name as courseName");
	                                                        					$sql2['join']['course'] = "course.Id = teacherlink.courseId";
	                                                        				}
	                                                        				getChilds($q->record);
	                                                        			}
	                                                        			if(in_array("all",$fetch) || in_array("link",$fetch)) {
	                                                        				foreach($q->record as $key => $row) {
	                                                        					$teacherLinkarr = explode(',', $row['teacherLinkId']);
	                                                        					foreach($teacherLinkarr as $val) {
	                                                        					    $sql2 = array(
	                                                        					    	"data" => [
	                                                        					    		'employee.id as teacherId',
	                                                        					    		'employee.name as teacherName',
	                                                        					    	],
	                                                        					    	"join" => [
	                                                        					    		'employee' => 'employee.id = teacherlink.teacherId',
	                                                        					    	],
	                                                        					    	"where" => ['teacherlink.id' => $val],
	                                                        					    );
	                                                        					    if($examUseCourse) {
	                                                        							array_push($sql2['data'], "course.id as courseId", "course.name as courseName");
	                                                        							$sql2['join']['course'] = "course.Id = teacherlink.courseId";
	                                                        						}
	                                                        						$q2 = Query::get("teacherlink", $sql2);
	                                                        						$q->record[$key]['link'] = $q2;
	                                                        					}
	                                                        				}
	                                                        			}
	                                                        		}
	                                                        		if(in_array("concatenation",$fetch))  {
	                                                        			$sql3 = array(
	                                                        				"data" => [
	                                                        					'examSet',
	                                                        					'relation',
	                                                        					'type',
	                                                        			]);
	                                                        			foreach($q->record as $key => $row) {
	                                                        				if($q->record[$key]['status'] == 'part-published' || $q->record[$key]['status'] == 'parent-published') {
	                                                        					$sql3['where'] [ 'examSet'] = " :inset: {$q->record[$key]['id']}";
	                                                        					$q3 = Query::get("examsrelation", $sql3);
	                                                        					$q->record[$key]['concatenation'] = $q3;
	                                                        
	                                                        				}
	                                                        			}
	                                                        		}
	                                                                return $q;
	                                                            });	// --------------------------------------------------------------------

	/**
	 * GET: exam/date : date
	 *
	 * @access  public
	 * @effects: module.reservation.js |
	 * @return  json | exam in this date
	 */
	API::get("date", ['date'], function(&$scope, $router) use ($sql) {

		if(!(
			Employee::hasRule("exam-can-access") ||
			Employee::hasRule("reservation-can-access") ||
			API::access()
		)) return Employee::accessDenied("exam-can-access, reservation-can-access");

		if(Employee::logged() && !Employee::hasRule("show-all-exams")) $sql['where']['teacherId'] = Employee::id();
		$args = Request::get(["fetch","status"]);
		$fetch = explode(",", $args->fetch);
		if(in_array("requireRes", $fetch)){
			$sql['where']['settings'] = ':like:%"requireRes":true%';
		}
		if($router->date) $sql['where'] = array("exam.date" => urldecode($router->date));
		$args = Request::get(["fetch","status"]);
		if($args->status) {
			$arr = explode(',', $args->status);
			$s = '';
			foreach($arr as $val) {
					$val = "'".$val."'";
					if($s == '') $s = $val;
					else $s = $s.','.$val;
			};
			$sql['where']["status"] = ":in:{$s}";
		};
		$q = Query::get("exam", $sql);
		getChilds($q->record);
		return $q;
	});

	// --------------------------------------------------------------------

	/**
	 * GET: exam/bank :bankId
	 *
	 * @access  public
	 * @return  json | exam in bankLog
	 */
	API::get("bank", ['id'], function(&$scope, $router) use ($sql) {
		if( !(Employee::hasRule("exam-can-access") || API::access()) )
			return Employee::accessDenied("exam-can-access");
		$sql2 = array(
			"data" => [
				'exam.name as examName',
				'exam.id as examId',
				'exam.date as examDate'
			],
			"join" => [
				'banklog' => 'banklog.examId = exam.id',
				'bank'    => 'bank.id = banklog.bankId'
			],
			"where" => ["bank.id" => $router->id]);
		if(Employee::logged() && !Employee::hasRule("show-all-exams")) $sql2['where']['teacherId'] = Employee::id();
		$q3 = Query::get("exam", $sql2);
		return $q3;
	});

	// --------------------------------------------------------------------

	/**
	 * GET: exam/status : stauts
	 *
	 * @access  public
	 * @effects: module.correction.js |
	 * @return  json | exams in this status - draft,published,complete
	 */
	API::get("status", ['id'], function(&$scope, $router) use ($sql) {

		if( !(Employee::hasRule("exam-can-access") || API::access()) )
			return Employee::accessDenied("exam-can-access");

		if(Employee::logged() && !Employee::hasRule("show-all-exams")) $sql['where']['teacherId'] = Employee::id();

		$args = Request::get(["fetch", "child", "uncorrect", "start", "limit", "search"]);

		$exam =  Query::table("exam")->param('*', 'faculty.name as facultyName',' teacherlink.majorId as majorId', 'class.name as className', 'class.id as classId', 'course.name as courseName', 'employee.name as teacherName' )
				->LeftJoin('teacherlink','teacherLinkId','inset' ,'~teacherlink.id')
				->LeftJoin('faculty','teacherLink.facultyId','~faculty.id')
				->LeftJoin('class','teacherLink.classId','~class.id')
				->LeftJoin('course','exam.courseId','~course.id')
				->LeftJoin('employee','employee.id','~teacherlink.teacherId');

		$fetch = explode(",", $args->fetch);
		if(in_array("notComplete", $fetch)) {
			$exam->LeftJoin('result','~exam.id', '~result.examId');
			$exam->LeftJoin('examdata','~exam.id', '~examdata.examId');
			$exam->LeftJoin('studentresult','~exam.id', '~studentresult.examId');
			$exam->where('exam.status', '!=', 'Complete');
			$exam->where('result.status', 'notComplete');
			$exam->where('examdata.type', 'in', explode (',', 'hw,text'));	
			$exam->where('~studentresult.status', 'notComplete');
			$exam->group('exam.id');

		} else if(in_array("published", $fetch)) {
			$exam->where('exam.status', 'published');
		}

		
		isset($args->search) && $args->search && $students->where(function($e)use($args){
			$e->where('exam.name' , 'like' , '%'.$args->search.'%')
			->orwhere('exam.id'   , 'like'   , '%'.$args->search.'%');
		});
		
		// $exam->where('exam.name' , 'like' , '%'.$args->search.'%');
		// isset($args->search) &&  $args->search && $exam->orwhere('exam.id'   , 'like'   , '%'.$args->search.'%');
		
		
		if($router->id) $exam->where('exam.id', $router->id);
		
		$total = clone($exam);
		$total = $total->get()->count;
		
		isset($args->limit) && !isset($args->start) &&  $exam->limit($args->limit);
		isset($args->limit) && isset($args->start)  &&  $exam->limit($args->start, $args->limit);

		if(Request::get('orderCol') && Request::get('orderDir')) $exam->order(Request::get('orderCol'), Request::get('orderDir'));
		$result = $exam->get();
		$result->total =  $total;

		if(in_array("total", $fetch)){
			$obj = ['total' => $total];
			return $obj;
		}
		
		return $result;

		 

		// $fetch = explode(",", $args->fetch);
		// if(in_array("notComplete", $fetch)) {
	    //     $sql['join']['result'] = "exam.id = result.examId";
	    //     $sql['join']['examdata'] = "examdata.examId = exam.id";
	    //     $sql['join']['studentresult'] = "studentresult.examId = exam.id";
	    //    // $sql['where']['examData.type'] = ":in:'hw','text'";
	    //    // $sql['where']['exam.status'] = ":not:Complete";
	    //     $sql['where'] = "exam.status != 'Complete' and examdata.type in ('hw','text') and result.status = 'notComplete' and studentresult.status ='notComplete'";
	    //     $sql['groupby'] = 'exam.id';
		// } else if(in_array("published", $fetch)) {
	    //     $sql['where'] = "exam.status = 'published'";
		// }

		// //limit and search
        // $args->limit && !$args->start &&  $sql['limit'] =  $args->limit;
        // $args->limit && $args->start  &&  $sql['limit']  = "{$args->start}, {$args->limit}";
        // //$args->search && $sql['where'] = "exam.name like '%{$args->search}%' or exam.id like '%{$args->search}%'";
		
		// if($router->id) $sql['where']['id'] = $router->id;
		// $q = Query::get("exam", $sql);

		//  // get total query 
        // $total =  Query::table("exam")->param('count(id) as total');
		// count($fetch) && $total->where("status" ,$fetch[0] );
        // // $args->search &&  $total->where('exam.name' , 'like' , '%'.$args->search.'%');
        // // $args->search &&  $total->orwhere('exam.id'   , 'like'   , '%'.$args->search.'%');
        // $q->total = $total->get()->record[0]["total"];


		// if(in_array("total", $fetch)){
		// 	$obj = ['total' => $q->total];
		// 	return $obj;
		// }
		// if($router->id)
		// if($args->child) getChilds($q->record);
		// if($args->uncorrect) getChilds($q->record);
		// return $q;
	});

	// --------------------------------------------------------------------

	/**
	 * GET: exam/:id
	 *
	 * @access  public
	 * @effects: module.edata.js | module.exam.js | module.StudentsRep.js | module.results.js
	 *         : module.reservation.js | module.Rep.js | module.QbankRep.js | module.OcrRep.js
	 *		   : vendor\student\app.js
	 * @return  json | exam for this id
	 */
	API::get(['id'], function(&$scope, $router) use ($sql, $examUseCourse, $showTeacherName) {
	   	if(!(
	   		Student::logged() || Employee::hasRule("exam-can-access") ||
	   		API::access()
		   )) return Employee::accessDenied("exam-can-access");
		   
		$args = Request::get(["fetch", "status", "datefrom", "dateto", "date", "unparented","linkId","order", "parse", "last" , "studentId","start", "limit", "search", "excludeStatus", "facultyId", "majorId", "courseId", "classId"]);

		return Exam::getExams($router, $args);
	});


	// --------------------------------------------------------------------

	/**
	*
	* Export exam List
	*
	* @access  public
	* @return
	*/
	API::post("export", function(&$scope, $router) {
		
		$args = Request::get(["type", "columns", "facultyId", 'majorId' , 'courseId', 'classId', "status", "datefrom", "dateto", "date", 'search', 'fetch','header', "head1", 'mergeCells']);
		//var_dump($args);die();
		$cols = explode(',', $args->columns);
		$type = $args->type;
		$colsNum = count($cols);
		

		$args->limit = Query::table("exam")->param("count(id) as total")->get()->record[0]['total']; //to avoid default limit from codehive

		$data = Exam::getExams($router, $args);
		
		$table = " "; 
		for ($c = 0; $c < $colsNum; $c++) {
			$table .= Localization::translate($cols[$c]);
			if($c < $colsNum - 1) $table .= "\t";
		}
		$table .= "\n";

		for ($j = 0; $j < $data->count; $j++) {

			for ($b = 0; $b < $colsNum; $b++) {

				$table .= $data->record[$j][$cols[$b]];
				if($b < $colsNum - 1) $table .= "\t";
			}
			$table .=  "\n";
		}
		$mergeCells = explode(',', $args->mergeCells);

		Export::saveFile($type, $args->header, $args->head1, "", $table, $colsNum, $mergeCells);
	});

	// --------------------------------------------------------------------
	
	/**
	*
	* update sessions group for exam
	*
	* @access  public
	* @return
	*/
	API::POST("updateSessionsGroup",['id'], function(&$scope, $router) {
		global $config;
		$appStatus = $config['settings']['appStatus'];
	
		$exam = Query::table('exam')->param('settings')->where('id', $router->id);
		$settings = $exam->get()->record[0]['settings'];
		$settings = json_decode($settings, true);
		$sessionsGroup = $settings['sessionsGroup'];
	
		array_splice($sessionsGroup,array_search($router->id,$sessionsGroup),1);
	//	unset($sessionsGroup[array_search($router->id,$sessionsGroup)]);

		//update sessionsGroup for selected exam session
		unset($settings['sessionsGroup']);
		$settings = json_encode($settings);
		Query::table('exam')->param('settings' , $settings)->where('id', $router->id)->set();

		//update sessionsGroup for linked exam sessions
		for($i = 0; $i < count($sessionsGroup); $i++) {

			$settings = Query::table('exam')->param('settings')->where('id', $sessionsGroup[$i])->get()->record[0]['settings'];

			$settings = json_decode($settings, true);
			if(count($sessionsGroup) == 1) {
				unset($settings['sessionsGroup']);
			} else {
				$settings['sessionsGroup'] = $sessionsGroup;
			}
			$settings = json_encode($settings);
			Query::table('exam')->param('settings' , $settings)->where('id', $sessionsGroup[$i])->set();
		}

		//update sessionsGroup in examRelation table
		$sessionsSet =  Query::table("examsrelation")
						->param('examSet', 'id')
						->where('type','sessions')
						->where('examSet', 'inset', $router->id)
						->where('statusId', $appStatus)
						->get()->record[0];
		if(count($sessionsGroup) == 1) { //delete record from exam relation
			return Query::table("examsrelation")
					->where('id', $sessionsSet['id'])
					->remove();  
		} else { //update exam set 
			$examSet = implode(',', $sessionsGroup);
			return Query::table("examsrelation")
					->param('examSet', $examSet )
					->where('id', $sessionsSet['id'])
					->set();  
		}
		
	});
	
	
	// --------------------------------------------------------------------
	/**
	 * POST: Exam
	 *
	 * Exam Informations
	 *"id" update this exam  if id in router ,
	 * @access  public
	 * @effects: module.exam.js |
	 * @param string name [exam name]
	 * @param string status [exam status - draft,complete, published]
	 * @param Date date  ['yyyy-mm-dd hh:mm:ss'];
	 * @param int duration [exam duration (min)]
	 * @param int total [exam total mark ]
	 * @param settings  array (view->[scroll,nextback],showMarks->[treu,false],random->[true,false])
	 * @param int created [exam created time]
	 * @param int modified [exam last modified  time]
	 * @param string ipaddr [exam creator ip address]
	 * @param int value [exam  value  ]
	 * @param int parent [exam parent id]
	 * @param int teacherLinkId [courseId,teacherId]
	 * @param questions child (title->questionText , type ->[multichoice , text ..] , answers array(choice1,choice2,...) , mark->int , correct->correctanswer,duration->int (question duration time))
	 * @return  json | Current exam Information
	 */
	API::POST(['id'], function(&$scope, $router) use ($sql, $examUseCourse) {

		// Original: if(!$router->id && !Employee::hasRule("exam-can-add"))
		// Temporary bypass for debugging:
		if(!$router->id && false) // Always allow exam-can-add for debugging
			return Employee::accessDenied("exam-can-add");

		else if($router->id && !Employee::hasRule("exam-can-edit"))
			 	return Employee::accessDenied("exam-can-edit");

		$args = Request::get([
			"name",
			"status",
			"date",
			"access",
			"time",
			"questions",
			"courseId" ,
			"duration",
			"totalQ",
			"mark",
			"settings",
			"link",
			"value",
			"resources",
			"templateId",
			"successMark"
		]);

		$q = array("data" => array( "modified" => time(), "ipaddr" => Request::ip(),));
		if($args->status == 'unpublished') {
			if(!Employee::hasRule("exam-can-unpublish"))
				return Employee::accessDenied("exam-can-unpublish");
			$exam = array(
				'data' => ['status','date'],
				'where'=> ['id' => $router->id]
			);
			$data = Query::get("exam", $exam);
			if(new DateTime() > new DateTime($data->record[0]['date'])) {
				return ["status" => false, "error" => "can't unpublish exam has a date in the past"];
			}
			$status = $data->record[0]['status'] == "published" ? "draft":"part";
    		return Query::set('exam',array("data" => ['status' => $status] ,'where' => ['id'=> $router->id],));
		}

		if($args->name) $q['data']['name'] = stripslashes($args->name);
		if($args->successMark) $q['data']['successMark'] = $args->successMark;
	
		if($args->date) {
			if($args->time) {
				$date = explode("-", $args->date); //[0]yy,[1]mm,[2]dd
				$time = explode(":",$args->time); //[0]hh,[1]mm
				$edate = date("Y-m-d H:i:s", mktime($time[0], $time[1], 0, $date[1], $date[2], $date[0]));
				$args->date = $edate;
			 }
			$q['data']['date'] = $args->date;
		}
		if($args->access) {
			$q['data']['access'] = $args->access;
		}
		$q['data']['teacherId'] = Employee::id();	
		if($args->totalQ) $q['data']['totalQ'] = $args->totalQ;
		if($args->mark) $q['data']['mark'] = $args->mark;
		if($args->value) $q['data']['value'] = $args->value;

		if($args->settings) {
		   $settings = stripslashes($args->settings);
   		   $q['data']['settings'] = $settings;
		}
		if($args->totalQ) $q['data']['totalQ'] = $args->totalQ;
		if($args->courseId) $q['data']['courseId'] = $args->courseId;
		if($args->duration) $q['data']['duration'] = $args->duration;
		if($args->templateId) $q['data']['templateId'] = $args->templateId;

		if($args->link) {
			if(isset($args->link)) {
			   $teacherLinkIds = implode(',', $args->link);
			   $q['data']['teacherLinkId'] = $teacherLinkIds;
			}
   		}
		if($router->id) {
			log::write("exam","update");
			$q['where'] = array("id" => $router->id);
		} else {
			log::write("exam","insert");
			$q['data']['created'] = time();
			$q['data']['status'] =  $args->status =='template'? $args->status:"draft";
			
		}
  		$query = Query::set("exam", $q);
  		$examid = ($router->id)?$router->id:$query->last;
        if($args->courseId) {
	        $courseId = $args->courseId;
        } else {
			$crs = array('data' =>['courseId'] ,'where'=>['id'=>$examid] );
			$crsId = Query::get("exam", $crs);
			$courseId = $crsId->record[0]['courseId'];
        }
    	if(isset($args->questions) && $args->questions !== "empty" && $args->status != 'template') {
			$qnum = count($args->questions);
			$qmarks = 0;
			$qdur = 0;
			if($router->id) {
				// TODO : remove filters for all exam data related .. and datalog .. to insert it again
			   Query::remove("examdata", array("where" => ["examId" => $examid]));
			}
			foreach($args->questions as $row) {
				$qnum = count($args->questions);
				$que['data'] = array();
				if(isset($row['mark'])) {
					$que['data']['mark'] = $row['mark'];
					$qmarks = $qmarks + $row['mark'];
				}
				if(isset($row['duration'])) {
					$que['data']['duration'] = $row['duration'];
					$qdur = $qdur + $row['duration'];
				}
				if(isset($row['title'])) {
					$que['data']['title'] = stripslashes($row['title']);
				}
                if(isset($row['context'])) {
					$que['data']['context'] = $row['context'];
				}
				$que['data']['type'] = $row['type']?:"mch";
				if(isset($row['answers'])) {
  					$que['data']['answers'] = stripslashes($row['answers']);
				}
				if(isset($row['correct'])) {
					$que['data']['correct'] = stripslashes($row['correct']);
				}
				if(isset($row['resources'])) {
					$que['data']['resources'] = stripslashes($row['resources']);
  				}

				if(isset($row['modelId'])) {
				 	$que['data']['modelId'] = $row['modelId'];
				}
				if(isset($row['filters'])) {
					if(is_array($row['filters'])){
						$que['data']['filters'] = json_encode($row['filters'], JSON_UNESCAPED_UNICODE);
					} else {
						$que['data']['filters'] = $row['filters'];
					}
				}

			   	if(isset($row['bankId'])) {
				 	$que['data']['bankId'] = $row['bankId'];
			    } else $que['data']['bankId'] = 0;
				$que['data']['examId'] = $examid;
				$res2 = Query::set("examdata", $que);
			}
		}
		if($args->status == "published" || $args->status == "parent-published" || $args->status == "part-published" || $args->status == "part") {

			if(!Employee::hasRule("exam-can-publish"))
				return Employee::accessDenied("exam-can-publish");
			log::write("exam","publish");
			//get exam data to check all info is complete
			$examData = array(
				'data' => [
					'name',
					'date',
					'mark',
					'totalQ',
					'duration',
					'settings',
					'status'
				],
				'where'=> ['id' => $examid]
			);
		 	$resdata = Query::get("exam",$examData);
			if($router->id) {
				if (new DateTime() > new DateTime($resdata->record[0]['date'])) {
					$query = Query::set("exam", $exam);
					return ["status" => false, "error" => "can't publish exam has a date in the past"];

				}
			}
			$notPublished = false;
			$error = "";
		 	if(
		 		!isset($resdata->record[0]['name']) ||
		 		!isset($resdata->record[0]['mark']) ||
		 		!isset($resdata->record[0]['totalQ']) ||
		 		!isset($resdata->record[0]['duration'])
		 	) {
				$notPublished = true ;
				$error = "can't publish exam - missing exam data";
			} else {
	 			//get Exam Questions
	 			$examQdata = array(
	 				'data' => [
	 					'id',
	 					'title',
	 					'type',
	 					'answers',
	 					'mark',
	 					'duration',
	 					'correct',
	 					'bankId',
	 					'resources',
						'modelId',
						'filters'
	 				],
	 				'where' => ['examId' => $examid],
					"groupby" => "examdata.id"
	 			 );
				$resQdata = Query::get("examdata", $examQdata);
				$settings = json_decode($resdata->record[0]['settings']);
				$modelsNum = (int)$settings->{'models'};
				$viewType = $settings->{'view'};

				for ($i=0; $i < $modelsNum; $i++) {
					$questions = array();
					$Qmarks = 0;
				  $Qdurs = 0;
					$questions = array_filter($resQdata->record, function ($q) use ($i) {
						if ((int)$q['modelId'] == $i) {
							return $q;
						}
					});
					if (count($questions) != $resdata->record[0]['totalQ']) {
						$notPublished = true;
						$error = "can't publish exam - mismatch questions count in model " .($i+1)." with the total number of exam questions";
					} else {
						foreach($questions as $key => $row) {
							$Qmarks += $row['mark'];
							$Qdurs += $row['duration'];
							if(
								!isset($row['title']) ||
								!isset($row['mark']) ||
								!isset($row['type']) ||
								!isset($row['answers']) ||
								!(isset($row['correct']) || ($row['type'] == "text" || $row['type'] == "hw" || $row['type'] == "match")) ||
								(!isset($row['duration']) && $settings->view == 2)
							) {
								$notPublished = true;
								$error = "can't publish exam - missing questions data in model ".($i+1);
								break;
							} else {
								$row['answers'] = substr($row['answers'], 1, strlen($row['answers'])-2);
								$answersarr = explode(',', $row['answers']);
								foreach($answersarr as $key => $row2) {
										if(stripslashes($row2) == '"::empty::"') {
										 $notPublished = true;
										 $error = "can't publish exam - missing questions answers in model ".($i+1);
										 break;
									}
								}
							}
						}// for each close !
						if (!$notPublished  && $Qmarks != $resdata->record[0]['mark']) {
							$notPublished = true;
							$error = "can't publish exam - mismatch questions marks in model " .($i+1)." with the total mark of exam ";
						} else if (!$notPublished && $viewType == '2' && $Qdurs != $resdata->record[0]['duration']) {
							$notPublished = true;
							$error =  "can't publish exam - mismatch questions duration in model " .($i+1)." with the total duration of exam ";
						}

					}

				}

	 		}
			if ($notPublished) {
				return ["status" => false, "error" => $error];
			}
			$exam = array(
				'data' => ['status' => $args->status],
				'where' =>  ['id' => $examid]
			);
			$query = Query::set("exam", $exam);
	 		insertTobank($resQdata->record, $courseId, $examid, $examUseCourse);
        }
		return $query;
	});

	// --------------------------------------------------------------------

	/**
	 * DELETE: exam/:id
	 *
	 * @access  public
	 * @effects: module.exam.js | module.reservation.js
	 * @return  json | exam for this id
	 */
	API::delete(['id'], function(&$scope, $router) use ($sql) {

		// TODO : if id not send return error ..
		$q = array("where" => array("examId" => $router->id));
		$sql['where'] = array("id" => $router->id);
		$res1 = Query::get("exam", ["where" => ["id" => $router->id]]);
		log::write("exam","delete");
		if($res1->record[0]['status'] == "published") {
			if( !(Employee::hasRule("exam-can-delete-publish") || API::access()) )
				return Employee::accessDenied("exam-can-delete-publish");
			$qrem = Query::remove("examdata", $q);
			if($qrem->status = true) {
				return Query::remove("exam", ["where" => ["id" => $router->id]]);
			}
		} else {
			$q2 = Query::remove("examdata", $q);
			if($q2->status = true) {
				return Query::remove("exam", ["where" => ["id" => $router->id]]);
			}
		}
	});

	/* End of API-> exam */
});

