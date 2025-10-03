import React, { useState } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Search, BookOpen, Stethoscope, Activity } from 'lucide-react';

const MedicalCodesCheatsheet = ({ trigger, onCodeSelect }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('icd10');
  const [open, setOpen] = useState(false);

  // Common ICD-10 Diagnosis Codes
  const icd10Codes = [
    { code: 'E11.9', description: 'Type 2 diabetes mellitus without complications', category: 'Endocrine' },
    { code: 'I10', description: 'Essential (primary) hypertension', category: 'Cardiovascular' },
    { code: 'J20.9', description: 'Acute bronchitis, unspecified', category: 'Respiratory' },
    { code: 'J45.9', description: 'Asthma, unspecified', category: 'Respiratory' },
    { code: 'M79.3', description: 'Panniculitis, unspecified', category: 'Musculoskeletal' },
    { code: 'M54.5', description: 'Low back pain', category: 'Musculoskeletal' },
    { code: 'M25.50', description: 'Pain in unspecified joint', category: 'Musculoskeletal' },
    { code: 'K59.00', description: 'Constipation, unspecified', category: 'Digestive' },
    { code: 'K21.9', description: 'Gastro-esophageal reflux disease without esophagitis', category: 'Digestive' },
    { code: 'R50.9', description: 'Fever, unspecified', category: 'Symptoms' },
    { code: 'R51', description: 'Headache', category: 'Neurological' },
    { code: 'J06.9', description: 'Acute upper respiratory infection, unspecified', category: 'Respiratory' },
    { code: 'Z00.00', description: 'Encounter for general adult medical examination without abnormal findings', category: 'Preventive' },
    { code: 'Z51.11', description: 'Encounter for antineoplastic chemotherapy', category: 'Treatment' },
    { code: 'I25.10', description: 'Atherosclerotic heart disease of native coronary artery without angina pectoris', category: 'Cardiac' },
    { code: 'L30.9', description: 'Dermatitis, unspecified', category: 'Skin' },
    { code: 'F32.9', description: 'Major depressive disorder, single episode, unspecified', category: 'Mental Health' },
    { code: 'N39.0', description: 'Urinary tract infection, site not specified', category: 'Genitourinary' },
    { code: 'H10.9', description: 'Unspecified conjunctivitis', category: 'Eye' },
    { code: 'G43.909', description: 'Migraine, unspecified, not intractable, without status migrainosus', category: 'Neurological' },
    { code: 'E78.5', description: 'Hyperlipidemia, unspecified', category: 'Endocrine' },
    { code: 'F41.9', description: 'Anxiety disorder, unspecified', category: 'Mental Health' },
    { code: 'J44.9', description: 'Chronic obstructive pulmonary disease, unspecified', category: 'Respiratory' },
    { code: 'N18.9', description: 'Chronic kidney disease, unspecified', category: 'Genitourinary' },
    { code: 'E66.9', description: 'Obesity, unspecified', category: 'Endocrine' }
  ];

  // Common CPT Procedure Codes
  const cptCodes = [
    { code: '99213', description: 'Office/outpatient visit, established patient, low complexity', category: 'Office Visits', price: '$150' },
    { code: '99214', description: 'Office/outpatient visit, established patient, moderate complexity', category: 'Office Visits', price: '$250' },
    { code: '99215', description: 'Office/outpatient visit, established patient, high complexity', category: 'Office Visits', price: '$350' },
    { code: '99202', description: 'Office/outpatient visit, new patient, straightforward', category: 'Office Visits', price: '$200' },
    { code: '99203', description: 'Office/outpatient visit, new patient, low complexity', category: 'Office Visits', price: '$275' },
    { code: '99204', description: 'Office/outpatient visit, new patient, moderate complexity', category: 'Office Visits', price: '$375' },
    { code: '85025', description: 'Blood count; complete (CBC), automated', category: 'Laboratory', price: '$50' },
    { code: '80053', description: 'Comprehensive metabolic panel', category: 'Laboratory', price: '$100' },
    { code: '80061', description: 'Lipid panel', category: 'Laboratory', price: '$75' },
    { code: '83036', description: 'Hemoglobin A1C test', category: 'Laboratory', price: '$100' },
    { code: '93000', description: 'Electrocardiogram, routine ECG with at least 12 leads', category: 'Cardiology', price: '$200' },
    { code: '93005', description: 'Electrocardiogram, tracing only, without interpretation', category: 'Cardiology', price: '$100' },
    { code: '36415', description: 'Collection of venous blood by venipuncture', category: 'Laboratory', price: '$25' },
    { code: '99396', description: 'Periodic comprehensive preventive medicine, established patient, 40-64 years', category: 'Preventive', price: '$300' },
    { code: '99397', description: 'Periodic comprehensive preventive medicine, established patient, 65+ years', category: 'Preventive', price: '$300' },
    { code: '76700', description: 'Abdominal ultrasound, complete', category: 'Radiology', price: '$400' },
    { code: '70450', description: 'CT head/brain without contrast', category: 'Radiology', price: '$800' },
    { code: '72148', description: 'MRI lumbar spine without contrast', category: 'Radiology', price: '$1200' },
    { code: '45378', description: 'Colonoscopy, flexible; diagnostic', category: 'Procedures', price: '$2500' },
    { code: '12001', description: 'Simple repair of superficial wounds, 2.5 cm or less', category: 'Surgery', price: '$300' },
    { code: '90471', description: 'Immunization administration (first injection)', category: 'Immunization', price: '$30' },
    { code: '90715', description: 'Tetanus, diphtheria toxoids and acellular pertussis vaccine (Tdap)', category: 'Immunization', price: '$75' },
    { code: '99281', description: 'Emergency department visit, self limited or minor problem', category: 'Emergency', price: '$400' },
    { code: '99283', description: 'Emergency department visit, moderate severity', category: 'Emergency', price: '$700' },
    { code: '96372', description: 'Therapeutic, prophylactic, or diagnostic injection', category: 'Procedures', price: '$100' }
  ];

  const filterCodes = (codes, searchTerm) => {
    if (!searchTerm) return codes;
    return codes.filter(item => 
      item.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.category.toLowerCase().includes(searchTerm.toLowerCase())
    );
  };

  const getCategoryColor = (category) => {
    const colors = {
      'Respiratory': 'bg-blue-100 text-blue-800',
      'Preventive': 'bg-green-100 text-green-800',
      'Cardiac': 'bg-red-100 text-red-800',
      'Cardiovascular': 'bg-red-100 text-red-800',
      'Treatment': 'bg-purple-100 text-purple-800',
      'Musculoskeletal': 'bg-orange-100 text-orange-800',
      'Digestive': 'bg-yellow-100 text-yellow-800',
      'Symptoms': 'bg-gray-100 text-gray-800',
      'Endocrine': 'bg-pink-100 text-pink-800',
      'Neurological': 'bg-indigo-100 text-indigo-800',
      'Skin': 'bg-amber-100 text-amber-800',
      'Mental Health': 'bg-violet-100 text-violet-800',
      'Genitourinary': 'bg-cyan-100 text-cyan-800',
      'Eye': 'bg-emerald-100 text-emerald-800',
      'Office Visits': 'bg-blue-100 text-blue-800',
      'Laboratory': 'bg-green-100 text-green-800',
      'Cardiology': 'bg-red-100 text-red-800',
      'Radiology': 'bg-purple-100 text-purple-800',
      'Procedures': 'bg-orange-100 text-orange-800',
      'Surgery': 'bg-red-100 text-red-800',
      'Immunization': 'bg-teal-100 text-teal-800',
      'Emergency': 'bg-rose-100 text-rose-800'
    };
    return colors[category] || 'bg-gray-100 text-gray-800';
  };

  const handleCodeClick = (code, description, type) => {
    if (onCodeSelect) {
      onCodeSelect({ code, description, type });
    }
  };

  const filteredICD10 = filterCodes(icd10Codes, searchTerm);
  const filteredCPT = filterCodes(cptCodes, searchTerm);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button variant="outline" className="gap-2">
            <BookOpen className="w-4 h-4" />
            Medical Codes Reference
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="max-w-4xl max-h-[85vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Stethoscope className="w-5 h-5 text-blue-600" />
            Medical Codes Cheatsheet
          </DialogTitle>
          <DialogDescription>
            Quick reference for ICD-10 diagnosis codes and CPT procedure codes. Click a code to use it.
          </DialogDescription>
        </DialogHeader>
        
        <div className="flex-1 overflow-hidden flex flex-col space-y-4">
          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <Input
              placeholder="Search by code, description, or category..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col overflow-hidden">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="icd10" className="flex items-center gap-2">
                <Activity className="w-4 h-4" />
                ICD-10 Diagnosis ({filteredICD10.length})
              </TabsTrigger>
              <TabsTrigger value="cpt" className="flex items-center gap-2">
                <Stethoscope className="w-4 h-4" />
                CPT Procedures ({filteredCPT.length})
              </TabsTrigger>
            </TabsList>

            <TabsContent value="icd10" className="flex-1 overflow-hidden mt-4">
              <Card className="h-full flex flex-col">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg">ICD-10 Diagnosis Codes</CardTitle>
                  <CardDescription>
                    International Classification of Diseases, 10th Revision
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex-1 overflow-y-auto">
                  <div className="space-y-2">
                    {filteredICD10.map((item, index) => (
                      <div 
                        key={index} 
                        className="p-3 border rounded-lg hover:bg-blue-50 hover:border-blue-300 cursor-pointer transition-colors"
                        onClick={() => handleCodeClick(item.code, item.description, 'icd10')}
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-mono font-semibold text-blue-600">{item.code}</span>
                              <Badge className={getCategoryColor(item.category)}>
                                {item.category}
                              </Badge>
                            </div>
                            <p className="text-sm text-gray-700">{item.description}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                    {filteredICD10.length === 0 && (
                      <div className="text-center py-8 text-gray-500">
                        No ICD-10 codes found matching "{searchTerm}"
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="cpt" className="flex-1 overflow-hidden mt-4">
              <Card className="h-full flex flex-col">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg">CPT Procedure Codes</CardTitle>
                  <CardDescription>
                    Current Procedural Terminology codes with typical pricing
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex-1 overflow-y-auto">
                  <div className="space-y-2">
                    {filteredCPT.map((item, index) => (
                      <div 
                        key={index} 
                        className="p-3 border rounded-lg hover:bg-green-50 hover:border-green-300 cursor-pointer transition-colors"
                        onClick={() => handleCodeClick(item.code, item.description, 'cpt')}
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-mono font-semibold text-green-600">{item.code}</span>
                              <Badge className={getCategoryColor(item.category)}>
                                {item.category}
                              </Badge>
                              {item.price && (
                                <span className="text-xs text-gray-600 font-medium ml-auto">
                                  ~{item.price}
                                </span>
                              )}
                            </div>
                            <p className="text-sm text-gray-700">{item.description}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                    {filteredCPT.length === 0 && (
                      <div className="text-center py-8 text-gray-500">
                        No CPT codes found matching "{searchTerm}"
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        <div className="pt-4 border-t">
          <p className="text-xs text-gray-500 text-center">
            💡 Tip: Click on any code to auto-fill it in your claim form
          </p>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default MedicalCodesCheatsheet;
